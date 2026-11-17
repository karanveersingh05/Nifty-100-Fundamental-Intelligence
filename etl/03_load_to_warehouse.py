import os
import sys
import pandas as pd
import numpy as np
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import get_engine
from core.models import Base, DimCompany, DimYear, DimSector, DimHealthLabel, FactBalanceSheet, FactProfitLoss, FactCashFlow, FactAnalysis, FactProsCons

# Pick the right dialect for upserts
_USE_SQLITE = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')
if _USE_SQLITE:
    from sqlalchemy.dialects.sqlite import insert
else:
    from sqlalchemy.dialects.postgresql import insert

CLEAN_DIR = 'data/clean/'

def clean_nan(df):
    """Replace NaN with None so SQLAlchemy handles NULLs correctly"""
    return df.replace({float('nan'): None})

def upsert_df(df, table_model, engine, index_elements):
    if df.empty:
        return 0
        
    df = df.drop_duplicates(subset=index_elements)
    df = clean_nan(df)
    records = df.to_dict(orient='records')
    
    # using an upsert here because I don't want duplicate entries if the script restarts
    stmt = insert(table_model).values(records)
    update_dict = {c.name: c for c in stmt.excluded if c.name not in index_elements}
    
    if update_dict:
        stmt = stmt.on_conflict_do_update(
            index_elements=index_elements,
            set_=update_dict
        )
    else:
        stmt = stmt.on_conflict_do_nothing(index_elements=index_elements)
        
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.rowcount

def load_data():
    engine = get_engine()
    
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(engine)
    
    summary = {}

    # 1. DimCompany
    print("\n--- Loading DimCompany ---")
    df_comp = pd.read_csv(os.path.join(CLEAN_DIR, 'companies.csv'))
    df_comp.rename(columns={'company_id': 'symbol'}, inplace=True)
    valid_cols = ['symbol', 'company_name', 'sector', 'sub_sector', 'company_logo', 'website', 'nse_url', 'bse_url', 'face_value', 'book_value', 'about_company']
    df_comp = df_comp[[c for c in valid_cols if c in df_comp.columns]]
    print(f"Before load: {len(df_comp)} rows to process.")
    try:
        upsert_df(df_comp, DimCompany, engine, ['symbol'])
        print("DimCompany loaded.")
    except Exception as e:
        print(f"Could not load to DB (is Docker running?): {e}")
        
    valid_symbols = set(df_comp['symbol'])
        
    # 2. DimYear
    print("\n--- Loading DimYear ---")
    df_bs_raw = pd.read_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'))
    df_year = df_bs_raw[['year_label', 'fiscal_year', 'sort_order']].drop_duplicates().dropna(subset=['fiscal_year'])
    df_year['year_id'] = df_year['fiscal_year'].astype(int)
    df_year['quarter'] = None
    df_year['is_ttm'] = df_year['year_label'] == 'TTM'
    df_year['is_half_year'] = False
    print(f"Before load: {len(df_year)} distinct years to process.")
    try:
        upsert_df(df_year, DimYear, engine, ['year_id'])
    except Exception:
        pass
        
    valid_years = set(df_year['year_id'])
        
    # 3. DimSector
    print("\n--- Loading DimSector ---")
    df_sec = pd.read_csv(os.path.join(CLEAN_DIR, 'sector_mapping.csv'))
    sectors = pd.DataFrame({'sector_name': df_sec['sector'].unique()})
    sectors['sector_code'] = sectors['sector_name'].str.upper().str[:4]
    print(f"Before load: {len(sectors)} sectors to process.")
    try:
        upsert_df(sectors, DimSector, engine, ['sector_name'])
    except Exception:
        pass

    # 4. DimHealthLabel
    print("\n--- Loading DimHealthLabel ---")
    health_labels = pd.DataFrame([
        {'label_name': 'EXCELLENT', 'min_score': 80.0, 'max_score': 100.0, 'color_hex': '#00FF00'},
        {'label_name': 'GOOD', 'min_score': 60.0, 'max_score': 79.9, 'color_hex': '#008000'},
        {'label_name': 'AVERAGE', 'min_score': 40.0, 'max_score': 59.9, 'color_hex': '#FFFF00'},
        {'label_name': 'WEAK', 'min_score': 20.0, 'max_score': 39.9, 'color_hex': '#FFA500'},
        {'label_name': 'POOR', 'min_score': 0.0, 'max_score': 19.9, 'color_hex': '#FF0000'}
    ])
    try:
        upsert_df(health_labels, DimHealthLabel, engine, ['label_name'])
    except Exception:
        pass

    # Fact Tables
    
    # FactBalanceSheet
    print("\n--- Loading FactBalanceSheet ---")
    df_bs = df_bs_raw.copy()
    df_bs.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_bs = df_bs.dropna(subset=['fiscal_year', 'symbol'])
    df_bs['year_id'] = df_bs['fiscal_year'].astype(int)
    
    # calculating debt-to-equity here so Power BI doesn't have to do the heavy lifting
    denom = df_bs['equity_capital'].fillna(0) + df_bs['reserves'].fillna(0)
    df_bs['debt_to_equity'] = np.where(denom != 0, df_bs['borrowings'].fillna(0) / denom, 0)
    df_bs['equity_ratio'] = np.where(df_bs['total_assets'].fillna(0) != 0, denom / df_bs['total_assets'], 0)
    
    bs_cols = ['symbol', 'year_id', 'equity_capital', 'reserves', 'borrowings', 'other_liabilities', 'total_liabilities', 'fixed_assets', 'cwip', 'investments', 'other_assets', 'total_assets', 'debt_to_equity', 'equity_ratio', 'book_value_per_share', 'asset_turnover', 'return_on_assets']
    df_bs = df_bs[[c for c in bs_cols if c in df_bs.columns]]
    df_bs = df_bs[df_bs['symbol'].isin(valid_symbols) & df_bs['year_id'].isin(valid_years)]
    print(f"Before load: {len(df_bs)} rows.")
    try:
        upsert_df(df_bs, FactBalanceSheet, engine, ['symbol', 'year_id'])
        summary['FactBalanceSheet'] = len(df_bs)
    except Exception as e:
        print(f"Error loading FactBalanceSheet: {e}")
        summary['FactBalanceSheet'] = 0

    # FactProfitLoss
    print("\n--- Loading FactProfitLoss ---")
    df_pl = pd.read_csv(os.path.join(CLEAN_DIR, 'profitandloss.csv'))
    df_pl.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_pl = df_pl.dropna(subset=['fiscal_year', 'symbol'])
    df_pl['year_id'] = df_pl['fiscal_year'].astype(int)
    
    # computing margins and ratios on the fly so dashboards are snappy
    df_pl['net_profit_margin_pct'] = np.where(df_pl['sales'].fillna(0) != 0, (df_pl['net_profit'].fillna(0) / df_pl['sales']) * 100, 0)
    df_pl['expense_ratio_pct'] = np.where(df_pl['sales'].fillna(0) != 0, (df_pl['expenses'].fillna(0) / df_pl['sales']) * 100, 0)
    df_pl['interest_coverage'] = np.where(df_pl['interest'].fillna(0) != 0, df_pl['operating_profit'].fillna(0) / df_pl['interest'], df_pl['operating_profit'].fillna(0))

    pl_cols = ['symbol', 'year_id', 'sales', 'expenses', 'operating_profit', 'opm_percentage', 'other_income', 'interest', 'depreciation', 'profit_before_tax', 'tax_percentage', 'net_profit', 'eps', 'dividend_payout', 'net_profit_margin_pct', 'expense_ratio_pct', 'interest_coverage']
    df_pl = df_pl[[c for c in pl_cols if c in df_pl.columns]]
    df_pl.rename(columns={'opm_percentage': 'opm_pct', 'tax_percentage': 'tax_pct', 'dividend_payout': 'dividend_payout_pct'}, inplace=True)
    df_pl = df_pl[df_pl['symbol'].isin(valid_symbols) & df_pl['year_id'].isin(valid_years)]
    print(f"Before load: {len(df_pl)} rows.")
    try:
        upsert_df(df_pl, FactProfitLoss, engine, ['symbol', 'year_id'])
        summary['FactProfitLoss'] = len(df_pl)
    except Exception as e:
        print(f"Error loading FactProfitLoss: {e}")
        summary['FactProfitLoss'] = 0

    # FactCashFlow
    print("\n--- Loading FactCashFlow ---")
    df_cf = pd.read_csv(os.path.join(CLEAN_DIR, 'cashflow.csv'))
    df_cf.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_cf = df_cf.dropna(subset=['fiscal_year', 'symbol'])
    df_cf['year_id'] = df_cf['fiscal_year'].astype(int)
    
    # calculating free cash flow directly during ETL
    df_cf['free_cash_flow'] = df_cf['operating_activity'].fillna(0) + df_cf['investing_activity'].fillna(0)

    cf_cols = ['symbol', 'year_id', 'operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow', 'free_cash_flow', 'cash_conversion_ratio']
    df_cf = df_cf[[c for c in cf_cols if c in df_cf.columns]]
    df_cf = df_cf[df_cf['symbol'].isin(valid_symbols) & df_cf['year_id'].isin(valid_years)]
    print(f"Before load: {len(df_cf)} rows.")
    try:
        upsert_df(df_cf, FactCashFlow, engine, ['symbol', 'year_id'])
        summary['FactCashFlow'] = len(df_cf)
    except Exception as e:
        print(f"Error loading FactCashFlow: {e}")
        summary['FactCashFlow'] = 0

    # FactAnalysis
    print("\n--- Loading FactAnalysis ---")
    df_an = pd.read_csv(os.path.join(CLEAN_DIR, 'analysis.csv'))
    df_an.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_an = df_an.dropna(subset=['symbol', 'period_label'])
    df_an = df_an[df_an['symbol'].isin(valid_symbols)]
    print(f"Before load: {len(df_an)} rows.")
    try:
        upsert_df(df_an, FactAnalysis, engine, ['symbol', 'period_label'])
        summary['FactAnalysis'] = len(df_an)
    except Exception as e:
        print(f"Error loading FactAnalysis: {e}")
        summary['FactAnalysis'] = 0

    # FactProsCons
    print("\n--- Loading FactProsCons ---")
    df_pc = pd.read_csv(os.path.join(CLEAN_DIR, 'prosandcons.csv'))
    df_pc.rename(columns={'company_id': 'symbol'}, inplace=True)
    df_pc = df_pc.dropna(subset=['symbol'])
    df_pc = df_pc[df_pc['symbol'].isin(valid_symbols)]
    print(f"Before load: {len(df_pc)} rows.")
    try:
        with engine.begin() as conn:
            conn.execute(FactProsCons.__table__.delete())
            records = clean_nan(df_pc).to_dict(orient='records')
            if records:
                conn.execute(insert(FactProsCons).values(records))
            summary['FactProsCons'] = len(df_pc)
    except Exception as e:
        print(f"Error loading FactProsCons: {e}")
        summary['FactProsCons'] = 0

    print("\nWarehouse Load Attempt Complete. Check logs for any connection errors if Docker is not up.")
    
    print("\n" + "="*40)
    print(" DATA WAREHOUSE LOAD SUMMARY")
    print("="*40)
    print(f"{'Fact Table':<25} | {'Rows Loaded':<10}")
    print("-" * 40)
    for table, count in summary.items():
        print(f"{table:<25} | {count:<10}")
    print("="*40)

if __name__ == "__main__":
    load_data()
