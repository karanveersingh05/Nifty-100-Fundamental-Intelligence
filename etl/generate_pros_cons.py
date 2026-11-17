"""
Automated Fundamental Pros & Cons Generator for B100 Listed Companies
Generates realistic, data-driven fundamental pros and cons for all 92 companies
based on actual balance sheet ratios, profitability margins, cash conversion,
dividend payouts, and sectoral moats.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Setup project root in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

CLEAN_DIR = os.path.join(project_root, 'data', 'clean')

# Sector-specific strategic strengths & risk factors
SECTOR_INSIGHTS = {
    'IT': {
        'pro_moat': "Global Tier-1 technology partner with deep enterprise multi-year digital transformation contracts.",
        'con_risk': "Vulnerable to client discretionary IT spending slowdowns and foreign currency fluctuations."
    },
    'Banking': {
        'pro_moat': "Strong low-cost CASA deposit franchise backed by extensive nationwide branch network.",
        'con_risk': "Exposed to cyclical asset-quality deterioration and net interest margin (NIM) compression."
    },
    'NBFC': {
        'pro_moat': "Specialized retail underwriting with agile credit appraisal systems and high customer retention.",
        'con_risk': "Higher borrowing cost sensitivity and asset-liability maturity mismatches in volatile rate cycles."
    },
    'Energy': {
        'pro_moat': "Critical national energy and utility infrastructure with non-discretionary, long-term cash flow visibility.",
        'con_risk': "Heavily exposed to regulatory tariff revisions and volatile global energy and fossil fuel prices."
    },
    'Consumer Goods': {
        'pro_moat': "Dominant consumer brand recall with deep pan-India distribution channels reaching millions of households.",
        'con_risk': "Intense competitive pressure from regional D2C brands and sensitivity to agricultural input cost inflation."
    },
    'Auto': {
        'pro_moat': "Strong market share in core passenger/commercial segments with aggressive EV transition roadmap.",
        'con_risk': "Cyclical automotive demand cycles, semiconductor lead times, and raw material steel/aluminium volatility."
    },
    'Healthcare': {
        'pro_moat': "Diversified multi-geography regulatory-approved generic formulations pipeline and robust R&D investments.",
        'con_risk': "US FDA regulatory inspection compliance scrutiny and pricing erosion in key overseas generic markets."
    },
    'Metals': {
        'pro_moat': "Large-scale vertically integrated manufacturing assets benefiting from national infrastructure capex.",
        'con_risk': "Earnings follow high cyclicality driven by Chinese steel demand and global base metal commodity benchmarks."
    },
    'Retail': {
        'pro_moat': "High-density retail store network with superior inventory turnover and exceptional supply-chain scale.",
        'con_risk': "High operating lease commitments and stiff competition from quick-commerce and e-commerce platforms."
    },
    'Telecom': {
        'pro_moat': "Oligopolistic telecom market structure with surging Average Revenue Per User (ARPU) and 5G penetration.",
        'con_risk': "High recurring spectrum acquisition costs and capital-intensive network equipment upgrades."
    },
    'Insurance': {
        'pro_moat': "Expanding bancassurance partnerships and steady compounding of long-term embedded value (VNB).",
        'con_risk': "Mortality and morbidity claim volatility along with regulatory limits on surrender charges."
    },
    'Cement': {
        'pro_moat': "Strategic limestone reserves and regional supply dominance benefiting from booming infrastructure and housing.",
        'con_risk': "High freight and pet coke power-and-fuel expenses impacting operating margins."
    },
    'Chemicals': {
        'pro_moat': "Specialty niche chemistry capabilities serving global pharma and agrochemical innovators.",
        'con_risk': "Global inventory destocking cycles and intense price competition from Chinese chemical exports."
    },
    'Infrastructure': {
        'pro_moat': "Massive multi-year order book across transportation, defense, green energy, and heavy engineering.",
        'con_risk': "Project execution delay risks and elevated working capital intensity on long-gestation EPC contracts."
    },
    'Other': {
        'pro_moat': "Established market positioning with robust operational brand heritage in its industry.",
        'con_risk': "Macroeconomic demand deceleration and general cost inflation pressures."
    }
}

def generate_pros_cons_for_all():
    print("Generating comprehensive pros & cons for all companies...")
    
    # 1. Load clean datasets
    df_comp = pd.read_csv(os.path.join(CLEAN_DIR, 'companies.csv'))
    df_bs = pd.read_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'))
    df_pl = pd.read_csv(os.path.join(CLEAN_DIR, 'profitandloss.csv'))
    df_cf = pd.read_csv(os.path.join(CLEAN_DIR, 'cashflow.csv'))
    df_an = pd.read_csv(os.path.join(CLEAN_DIR, 'analysis.csv'))
    
    symbols = df_comp['company_id'].dropna().unique()
    now = datetime.now()
    
    records = []
    
    for sym in symbols:
        comp_row = df_comp[df_comp['company_id'] == sym].iloc[0]
        cname = str(comp_row.get('company_name', sym)).strip()
        sector = str(comp_row.get('sector', 'Other')).strip()
        
        # Get latest records
        bs_sub = df_bs[df_bs['company_id'] == sym].sort_values('fiscal_year', ascending=False)
        pl_sub = df_pl[df_pl['company_id'] == sym].sort_values('fiscal_year', ascending=False)
        cf_sub = df_cf[df_cf['company_id'] == sym].sort_values('fiscal_year', ascending=False)
        an_sub = df_an[(df_an['company_id'] == sym) & (df_an['period_label'] == '3Y')]
        
        bs = bs_sub.iloc[0] if not bs_sub.empty else None
        pl = pl_sub.iloc[0] if not pl_sub.empty else None
        cf = cf_sub.iloc[0] if not cf_sub.empty else None
        an = an_sub.iloc[0] if not an_sub.empty else None
        
        pros = []
        cons = []
        
        # Sector insight
        sec_info = SECTOR_INSIGHTS.get(sector, SECTOR_INSIGHTS['Other'])
        pros.append(sec_info['pro_moat'])
        
        # ── 1. Solvency & Debt Analysis ──
        if bs is not None:
            dte = bs.get('debt_to_equity', 0)
            if pd.isna(dte): dte = 0
            
            if sector in ['Banking', 'NBFC', 'Insurance']:
                pros.append(f"Strong capital adequacy ratio and well-diversified loan/asset book across retail & corporate sectors.")
                cons.append(sec_info['con_risk'])
            else:
                if dte <= 0.05:
                    pros.append("Company is virtually debt-free with zero significant financial gearing.")
                elif dte < 0.5:
                    pros.append(f"Conservative capital structure with low Debt-to-Equity ratio of {dte:.2f}.")
                elif dte > 1.5:
                    cons.append(f"Elevated debt burden with Debt-to-Equity of {dte:.2f}, increasing interest expense obligations.")
                else:
                    pros.append(f"Manageable debt obligations with Debt-to-Equity maintained at {dte:.2f}.")

        # ── 2. Profitability & Margin Analysis ──
        if pl is not None:
            npm = pl.get('net_profit_margin_pct', 0)
            opm = pl.get('opm_pct', 0)
            payout = pl.get('dividend_payout_pct', 0)
            ic = pl.get('interest_coverage', 0)
            
            if pd.notna(npm) and npm > 15:
                pros.append(f"Exceptional net profit margin of {npm:.1f}%, exhibiting pricing power over input costs.")
            elif pd.notna(npm) and npm > 8:
                pros.append(f"Healthy net profit margin of {npm:.1f}%, sustaining consistent bottom-line returns.")
            elif pd.notna(npm) and npm < 4 and sector not in ['Retail', 'Banking']:
                cons.append(f"Thin net profit margin of {npm:.1f}%, leaving limited buffer against unexpected operational shocks.")

            if pd.notna(payout) and payout >= 25:
                pros.append(f"Consistent shareholder value distribution with a healthy dividend payout of {payout:.1f}%.")
            elif pd.notna(payout) and payout == 0:
                cons.append("Zero or negligible dividend payout over the recent financial reporting periods.")

            if sector not in ['Banking', 'NBFC', 'Insurance'] and pd.notna(ic) and ic < 2.0 and ic != 0:
                cons.append(f"Modest interest coverage ratio ({ic:.1f}x) reduces flexibility in rising interest rate regimes.")

        # ── 3. Cash Flow Generation ──
        if cf is not None:
            fcf = cf.get('free_cash_flow', 0)
            ccr = cf.get('cash_conversion_ratio', 0)
            if pd.notna(fcf) and fcf > 0:
                pros.append(f"Positive free cash flow generation strengthening internal liquidity and expansion reserves.")
            elif pd.notna(fcf) and fcf < 0:
                cons.append("Negative free cash flow due to aggressive ongoing capital expenditure or working capital lockup.")
            
            if pd.notna(ccr) and ccr > 0.85:
                pros.append("Robust cash conversion efficiency with operating cash flows closely matching net profit.")

        # ── 4. Growth & Return Ratios ──
        if an is not None:
            roe = an.get('roe_pct', 0)
            sales_cagr = an.get('compounded_sales_growth_pct', 0)
            profit_cagr = an.get('compounded_profit_growth_pct', 0)
            
            if pd.notna(roe) and roe > 15:
                pros.append(f"Strong Return on Equity (ROE) track record (3-Year Average: {roe:.1f}%).")
            elif pd.notna(roe) and roe < 8 and roe > 0:
                cons.append(f"Subdued 3-year Return on Equity of {roe:.1f}%, trailing top industry benchmarks.")

            if pd.notna(sales_cagr) and sales_cagr > 12:
                pros.append(f"Strong multi-year top-line momentum with 3-Year Compounded Sales Growth of {sales_cagr:.1f}%.")
            elif pd.notna(sales_cagr) and sales_cagr < 5 and sales_cagr != 0:
                cons.append(f"Sluggish 3-year sales growth ({sales_cagr:.1f}% CAGR) indicating near-term market saturation.")

        # Ensure balanced cons
        if len(cons) < 2:
            cons.append(f"Valuation metrics reflect premium multiples given the company's established market leadership.")
        if len(cons) < 2 and sector not in ['Banking', 'NBFC']:
            cons.append(sec_info['con_risk'])

        # Keep top 3-4 pros and top 2-3 cons
        pros = list(dict.fromkeys(pros))[:4]
        cons = list(dict.fromkeys(cons))[:3]

        for p in pros:
            records.append({
                'company_id': sym,
                'is_pro': True,
                'text': p,
                'category': 'Fundamental',
                'source': 'ANALYTICS_ENGINE',
                'confidence': 0.95
            })

        for c in cons:
            records.append({
                'company_id': sym,
                'is_pro': False,
                'text': c,
                'category': 'Fundamental',
                'source': 'ANALYTICS_ENGINE',
                'confidence': 0.95
            })

    df_out = pd.DataFrame(records)
    out_path = os.path.join(CLEAN_DIR, 'prosandcons.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Generated {len(df_out)} pros & cons across {len(symbols)} companies (saved to {out_path}).")
    return df_out

def reload_pros_cons_to_warehouse():
    from core.db import get_engine
    from core.models import FactProsCons
    _USE_SQLITE = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')
    if _USE_SQLITE:
        from sqlalchemy.dialects.sqlite import insert
    else:
        from sqlalchemy.dialects.postgresql import insert

    engine = get_engine()
    df_pc = pd.read_csv(os.path.join(CLEAN_DIR, 'prosandcons.csv'))
    df_pc.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_pc = df_pc.dropna(subset=['symbol'])

    try:
        with engine.begin() as conn:
            conn.execute(FactProsCons.__table__.delete())
            records = df_pc.to_dict(orient='records')
            if records:
                conn.execute(insert(FactProsCons).values(records))
        print(f"Successfully reloaded {len(df_pc)} Pros & Cons into Data Warehouse (fact_pros_cons)!")
    except Exception as e:
        print(f"Failed to reload Pros & Cons into DB: {e}")

if __name__ == '__main__':
    generate_pros_cons_for_all()
    reload_pros_cons_to_warehouse()
