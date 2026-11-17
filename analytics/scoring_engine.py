import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import text

_USE_SQLITE = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')
if _USE_SQLITE:
    from sqlalchemy.dialects.sqlite import insert
else:
    from sqlalchemy.dialects.postgresql import insert

# Setup path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import get_engine
from core.models import FactMLScores, DimCompany

class CompanyScorer:
    def __init__(self, engine):
        self.engine = engine
        
    def fetch_data(self):
        # We need data from fact_profit_loss, fact_balance_sheet, fact_cash_flow, fact_analysis
        # We will load them into pandas for easy scoring calculation.
        
        # Using a raw query for speed and joins
        query = """
        SELECT 
            c.symbol,
            pl.year_id,
            pl.sales,
            pl.net_profit,
            pl.opm_pct,
            pl.net_profit_margin_pct,
            pl.interest_coverage,
            pl.dividend_payout_pct,
            bs.debt_to_equity,
            cf.free_cash_flow,
            cf.cash_conversion_ratio,
            an.compounded_sales_growth_pct,
            an.compounded_profit_growth_pct,
            an.roe_pct,
            y.is_ttm
        FROM dim_company c
        LEFT JOIN fact_profit_loss pl ON c.symbol = pl.symbol
        LEFT JOIN fact_balance_sheet bs ON c.symbol = bs.symbol AND pl.year_id = bs.year_id
        LEFT JOIN fact_cash_flow cf ON c.symbol = cf.symbol AND pl.year_id = cf.year_id
        LEFT JOIN dim_year y ON pl.year_id = y.year_id
        LEFT JOIN fact_analysis an ON c.symbol = an.symbol AND an.period_label = '3Y'
        """
        try:
            return pd.read_sql(query, self.engine)
        except Exception as e:
            print(f"Failed to fetch data from DB: {e}")
            print("Falling back to CSVs to keep the scoring engine resilient during dev testing...")
            # Fallback to CSVs if DB is not available
            CLEAN_DIR = 'data/clean/'
            pl = pd.read_csv(os.path.join(CLEAN_DIR, 'profitandloss.csv'))
            bs = pd.read_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'))
            cf = pd.read_csv(os.path.join(CLEAN_DIR, 'cashflow.csv'))
            an = pd.read_csv(os.path.join(CLEAN_DIR, 'analysis.csv'))
            comp = pd.read_csv(os.path.join(CLEAN_DIR, 'companies.csv'))
            
            # ensure year_id
            pl['year_id'] = pl['fiscal_year'].fillna(9999).astype(int)
            bs['year_id'] = bs['fiscal_year'].fillna(9999).astype(int)
            cf['year_id'] = cf['fiscal_year'].fillna(9999).astype(int)
            
            # Add is_ttm logic based on fiscal_year = 9999
            pl['is_ttm'] = pl['year_id'] == 9999
            
            an_3y = an[an['period_label'] == '3Y'].copy()
            
            # build dataframe mimicking the SQL result
            df = comp[['company_id']].rename(columns={'company_id': 'symbol'})
            df = pl.merge(df, on='symbol', how='inner')
            df = df.merge(bs[['symbol', 'year_id', 'debt_to_equity']], on=['symbol', 'year_id'], how='left')
            df = df.merge(cf[['symbol', 'year_id', 'free_cash_flow', 'cash_conversion_ratio']], on=['symbol', 'year_id'], how='left')
            df = df.merge(an_3y[['symbol', 'compounded_sales_growth_pct', 'compounded_profit_growth_pct', 'roe_pct']], on='symbol', how='left')
            
            return df
            
    def compute_scores(self, df):
        if df is None or df.empty:
            return pd.DataFrame()
            
        symbols = df['symbol'].unique()
        results = []
        
        now = datetime.now()
        
        for sym in symbols:
            comp_data = df[df['symbol'] == sym]
            if comp_data.empty:
                continue
                
            # Get TTM or latest data
            ttm_data = comp_data[comp_data['is_ttm'] == True]
            if ttm_data.empty:
                # Get the row with max year_id
                if not comp_data['year_id'].dropna().empty:
                    latest = comp_data.loc[comp_data['year_id'].idxmax()]
                else:
                    latest = comp_data.iloc[-1]
            else:
                latest = ttm_data.iloc[0]
                
            # 1. Profitability (0-100)
            roe = latest.get('roe_pct', 0)
            npm = latest.get('net_profit_margin_pct', 0)
            prof_score = np.clip(((roe or 0) * 2) + ((npm or 0) * 2), 0, 100)
            if pd.isna(prof_score): prof_score = 50.0
            
            # 2. Growth (0-100)
            # calculating a growth score here-if sales CAGR is < 5%, they're basically a zombie company
            sales_cagr = latest.get('compounded_sales_growth_pct', 0)
            profit_cagr = latest.get('compounded_profit_growth_pct', 0)
            sales_cagr = 0 if pd.isna(sales_cagr) else sales_cagr
            profit_cagr = 0 if pd.isna(profit_cagr) else profit_cagr
            
            if sales_cagr < 5:
                growth_score = min(20, max(0, sales_cagr * 4)) # zombie penalty
            else:
                growth_score = np.clip((sales_cagr * 3) + (profit_cagr * 2), 0, 100)
            
            # 3. Leverage (0-100) -> Lower debt is better
            dte = latest.get('debt_to_equity', 0)
            ic = latest.get('interest_coverage', 0)
            dte = 0 if pd.isna(dte) else dte
            ic = 0 if pd.isna(ic) else ic
            
            lev_score = 100
            if dte > 2: lev_score -= 50
            elif dte > 1: lev_score -= 25
            
            if ic < 1: lev_score -= 50
            elif ic < 3: lev_score -= 20
            
            lev_score = np.clip(lev_score, 0, 100)
            
            # 4. Cash Flow (0-100)
            fcf = latest.get('free_cash_flow', 0)
            ccr = latest.get('cash_conversion_ratio', 0)
            fcf = 0 if pd.isna(fcf) else fcf
            ccr = 0 if pd.isna(ccr) else ccr
            
            cf_score = 50
            if fcf > 0: cf_score += 25
            if ccr > 0.8: cf_score += 25
            cf_score = np.clip(cf_score, 0, 100)
            
            # 5. Dividends (0-100)
            payout = latest.get('dividend_payout_pct', 0)
            payout = 0 if pd.isna(payout) else payout
            div_score = np.clip(payout * 2, 0, 100)
            
            # 6. Trend Score: TTM vs 3-year average
            # Compare latest net profit against 3-year historical average to see if they are improving or sliding
            hist = comp_data[comp_data['is_ttm'] == False].sort_values('year_id', ascending=False).head(3)
            if not hist.empty and not pd.isna(latest.get('net_profit', 0)):
                avg_profit = hist['net_profit'].mean()
                if avg_profit != 0:
                    trend_ratio = (latest['net_profit'] - avg_profit) / abs(avg_profit)
                    trend_score = np.clip(50 + (trend_ratio * 100), 0, 100)
                else:
                    trend_score = 50.0
            else:
                trend_score = 50.0
                
            # Overall Score weighted blend
            overall_score = (prof_score * 0.25) + (growth_score * 0.25) + (lev_score * 0.2) + (cf_score * 0.15) + (trend_score * 0.15)
            overall_score = round(overall_score, 2)
            
            # mapping the health label so the frontend can just grab a color_hex and go
            if overall_score >= 80:
                health_label = 'EXCELLENT'
            elif overall_score >= 60:
                health_label = 'GOOD'
            elif overall_score >= 40:
                health_label = 'AVERAGE'
            elif overall_score >= 20:
                health_label = 'WEAK'
            else:
                health_label = 'POOR'
                
            results.append({
                'symbol': sym,
                'computed_at': now,
                'overall_score': overall_score,
                'profitability_score': round(prof_score, 2),
                'growth_score': round(growth_score, 2),
                'leverage_score': round(lev_score, 2),
                'cashflow_score': round(cf_score, 2),
                'dividend_score': round(div_score, 2),
                'trend_score': round(trend_score, 2),
                'health_label': health_label
            })
            
        return pd.DataFrame(results)

    def load_to_db(self, scores_df):
        if scores_df.empty:
            print("No scores to load.")
            return
            
        records = scores_df.to_dict(orient='records')
        
        try:
            with self.engine.begin() as conn:
                # Clear previous run to prevent duplicate company entries in dashboard
                conn.execute(FactMLScores.__table__.delete())
                conn.execute(insert(FactMLScores).values(records))
            print(f"Successfully loaded {len(records)} score records to fact_ml_scores.")
        except Exception as e:
            print(f"DB load failed (DB offline?): {e}")

def run():
    print("Initializing Scoring Engine...")
    engine = get_engine()
    scorer = CompanyScorer(engine)
    
    print("Fetching raw data from Fact tables...")
    df = scorer.fetch_data()
    
    print("Calculating ML Health Scores and Trends...")
    scores_df = scorer.compute_scores(df)
    
    if not scores_df.empty:
        scorer.load_to_db(scores_df)
        
        print("\n" + "="*50)
        print("🧠 B100 INTELLIGENCE: HEALTH SCORE SMOKE TEST")
        print("="*50)
        
        # Top 5
        print("\n📈 TOP 5 'EXCELLENT' COMPANIES:")
        top_5 = scores_df[scores_df['health_label'] == 'EXCELLENT'].nlargest(5, 'overall_score')
        if top_5.empty:
            top_5 = scores_df.nlargest(5, 'overall_score')
            
        for _, row in top_5.iterrows():
            print(f"⭐ {row['symbol']:<12} | Score: {row['overall_score']:>6.2f} | Growth: {row['growth_score']:>6.2f} | Trend: {row['trend_score']:>6.2f}")
            
        # Bottom 5
        print("\n📉 BOTTOM 5 'POOR' COMPANIES:")
        bottom_5 = scores_df[scores_df['health_label'] == 'POOR'].nsmallest(5, 'overall_score')
        if bottom_5.empty:
            bottom_5 = scores_df.nsmallest(5, 'overall_score')
            
        for _, row in bottom_5.iterrows():
            print(f"⚠️ {row['symbol']:<12} | Score: {row['overall_score']:>6.2f} | Growth: {row['growth_score']:>6.2f} | Leverage: {row['leverage_score']:>6.2f}")
            
        print("\nDone. Engine has finished scoring.")
    else:
        print("Failed to compute scores (no data found).")

if __name__ == "__main__":
    run()
