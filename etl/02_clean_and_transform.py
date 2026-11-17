import pandas as pd
import numpy as np
import re
import os

# Paths
RAW_DIR = 'data/raw/'
CLEAN_DIR = 'data/clean/'

def clean_year_column(df, year_col='year'):
    # Creates 'year_label', 'fiscal_year', 'sort_order'
    if year_col not in df.columns:
        return df
        
    def parse_year(y):
        if pd.isna(y): return None, None, 999
        y_str = str(y).strip()
        if y_str.upper() in ['TTM', 'LATEST']:
            return 'TTM', 9999, 9999
            
        match = re.search(r'([a-zA-Z]+)[- ]?(\d{2,4})', y_str)
        if match:
            month = match.group(1).title()
            yr_str = match.group(2)
            yr = 2000 + int(yr_str) if len(yr_str) == 2 else int(yr_str)
            return f"{month} {yr}", yr, yr
        return y_str, None, 999

    parsed = df[year_col].apply(parse_year)
    df['year_label'] = [x[0] for x in parsed]
    df['fiscal_year'] = [x[1] for x in parsed]
    df['sort_order'] = [x[2] for x in parsed]
    return df

def extract_percent(val):
    if pd.isna(val): return np.nan
    val_str = str(val).strip()
    if val_str.lower() in ['null', 'nan', '']: return np.nan
    
    # Extract number before % sign or just the number
    match = re.search(r'(-?\d+(?:\.\d+)?)%?', val_str)
    if match:
        return float(match.group(1))
    return np.nan

def extract_period(val):
    if pd.isna(val): return None
    val_str = str(val).strip().lower()
    
    label = val_str.split(':')[0] if ':' in val_str else val_str
    
    if '10' in label: return '10Y'
    if '5' in label: return '5Y'
    if '3' in label: return '3Y'
    if '1' in label or 'last' in label or 'ttm' in label: return 'TTM'
    return None

def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    
    # 1. Clean Companies & Sector Classification
    print("Cleaning companies...")
    df_comp = pd.read_csv(os.path.join(RAW_DIR, 'companies.csv'))
    if 'id' in df_comp.columns and 'company_id' not in df_comp.columns:
        df_comp.rename(columns={
            'id': 'company_id', 
            'nse_profile': 'nse_url', 
            'bse_profile': 'bse_url'
        }, inplace=True)
        
    # simple check for nulls here
    df_comp.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    
    # Strip trailing whitespace and \r\n from company_name
    if 'company_name' in df_comp.columns:
        df_comp['company_name'] = df_comp['company_name'].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
    
    # finally finished the sector mapping-no more 'NULL' values in the frontend
    sector_map = {
        'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HCLTECH': 'IT', 'TECHM': 'IT', 'LTIM': 'IT', 'PERSISTENT': 'IT', 'COFORGE': 'IT', 'MPHASIS': 'IT', 'OFSS': 'IT',
        'HDFCBANK': 'Banking', 'AXISBANK': 'Banking', 'BANKBARODA': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'KOTAKBANK': 'Banking', 'INDUSINDBK': 'Banking', 'PNB': 'Banking', 'CANBK': 'Banking', 'IDFCFIRSTB': 'Banking', 'YESBANK': 'Banking', 'UNIONBANK': 'Banking', 'IOB': 'Banking', 'INDIANB': 'Banking',
        'ADANIGREEN': 'Energy', 'ADANIPOWER': 'Energy', 'ADANIENSOL': 'Energy', 'ATGL': 'Energy', 'NTPC': 'Energy', 'ONGC': 'Energy', 'POWERGRID': 'Energy', 'BPCL': 'Energy', 'IOC': 'Energy', 'HINDPETRO': 'Energy', 'GAIL': 'Energy', 'COALINDIA': 'Energy', 'OIL': 'Energy', 'PETRONET': 'Energy',
        'AMBUJACEM': 'Cement', 'ULTRACEMCO': 'Cement', 'SHREECEM': 'Cement', 'GRASIM': 'Cement', 'DALBHARAT': 'Cement', 'RAMCOCEM': 'Cement', 'ACC': 'Cement', 'JKCEMENT': 'Cement',
        'APOLLOHOSP': 'Healthcare', 'SUNPHARMA': 'Healthcare', 'CIPLA': 'Healthcare', 'DRREDDY': 'Healthcare', 'DIVISLAB': 'Healthcare', 'LUPIN': 'Healthcare', 'AUROPHARMA': 'Healthcare', 'BIOCON': 'Healthcare', 'MAXHEALTH': 'Healthcare', 'SYNGENE': 'Healthcare', 'ZYDUSLIFE': 'Healthcare', 'TORNTPHARM': 'Healthcare',
        'ASIANPAINT': 'Consumer Goods', 'BRITANNIA': 'Consumer Goods', 'HUL': 'Consumer Goods', 'ITC': 'Consumer Goods', 'NESTLEIND': 'Consumer Goods', 'TATACONSUM': 'Consumer Goods', 'TITAN': 'Consumer Goods', 'DABUR': 'Consumer Goods', 'GODREJCP': 'Consumer Goods', 'MARICO': 'Consumer Goods', 'COLPAL': 'Consumer Goods', 'BERGEPAINT': 'Consumer Goods', 'UBL': 'Consumer Goods', 'UNITEDSPR': 'Consumer Goods', 'PGHH': 'Consumer Goods',
        'SBILIFE': 'Insurance', 'HDFCLIFE': 'Insurance', 'ICICIGI': 'Insurance', 'ICICIPRULI': 'Insurance', 'LICI': 'Insurance', 'STARHEALTH': 'Insurance', 'GICRE': 'Insurance', 'NIACL': 'Insurance',
        'BAJAJ-AUTO': 'Auto', 'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'M&M': 'Auto', 'EICHERMOT': 'Auto', 'HEROMOTOCO': 'Auto', 'TVSMOTOR': 'Auto', 'BOSCHLTD': 'Auto', 'MOTHERSON': 'Auto', 'MRF': 'Auto', 'ASHOKLEY': 'Auto', 'TIINDIA': 'Auto', 'BALKRISIND': 'Auto',
        'BAJFINANCE': 'NBFC', 'BAJAJFINSV': 'NBFC', 'CHOLAFIN': 'NBFC', 'MUTHOOTFIN': 'NBFC', 'SHRIRAMFIN': 'NBFC', 'BAJAJHLDNG': 'NBFC', 'PFC': 'NBFC', 'RECLTD': 'NBFC', 'IRFC': 'NBFC', 'M&MFIN': 'NBFC', 'SUNDARMFIN': 'NBFC', 'L&TFH': 'NBFC', 'POONAWALLA': 'NBFC',
        'RELIANCE': 'Conglomerate', 'LT': 'Infrastructure', 'BHARTIARTL': 'Telecom', 'IDEA': 'Telecom', 'INDUSINDS': 'Telecom',
        'TATASTEEL': 'Metals', 'JSWSTEEL': 'Metals', 'HINDALCO': 'Metals', 'VEDL': 'Metals', 'NMDC': 'Metals', 'SAIL': 'Metals', 'JINDALSTEL': 'Metals', 'NATIONALUM': 'Metals', 'HINDZINC': 'Metals',
        'UPL': 'Chemicals', 'PIIND': 'Chemicals', 'SRF': 'Chemicals', 'AARTIIND': 'Chemicals', 'DEEPAKNTR': 'Chemicals', 'NAVINFLUOR': 'Chemicals', 'TATACHEM': 'Chemicals', 'COROMANDEL': 'Chemicals',
        'DMART': 'Retail', 'TRENT': 'Retail', 'ZOMATO': 'Consumer Services', 'NYKAA': 'Consumer Services', 'PAYTM': 'Financial Technology', 'POLICYBZR': 'Financial Technology',
        'DLF': 'Real Estate', 'MACROTECH': 'Real Estate', 'GODREJPROP': 'Real Estate', 'OBEROIRLTY': 'Real Estate',
        'IRCTC': 'Tourism & Hospitality', 'INDIGO': 'Aviation', 'AWL': 'FMCG'
    }
    
    df_comp['sector'] = df_comp['company_id'].map(sector_map).fillna('Other')
    df_comp['sub_sector'] = 'General'
    df_comp.to_csv(os.path.join(CLEAN_DIR, 'companies.csv'), index=False)
    
    sector_df = df_comp[['company_id', 'sector']].drop_duplicates()
    sector_df.to_csv(os.path.join(CLEAN_DIR, 'sector_mapping.csv'), index=False)
    
    # 2. Clean Balance Sheet
    print("Cleaning balance sheet...")
    df_bs = pd.read_csv(os.path.join(RAW_DIR, 'balancesheet.csv'))
    df_bs.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    df_bs = clean_year_column(df_bs, 'year')
    
    df_bs.rename(columns={'other_asset': 'other_assets'}, inplace=True)
    num_cols_bs = ['equity_capital', 'reserves', 'borrowings', 'other_liabilities', 'total_liabilities', 'fixed_assets', 'cwip', 'investments', 'other_assets', 'total_assets']
    for col in num_cols_bs:
        if col in df_bs.columns:
            df_bs[col] = pd.to_numeric(df_bs[col], errors='coerce').fillna(0)
            
    # debt_to_equity
    denom = (df_bs['equity_capital'] + df_bs['reserves'])
    df_bs['debt_to_equity'] = np.where(denom != 0, df_bs['borrowings'] / denom, 0)
    df_bs['equity_ratio'] = np.where(df_bs['total_assets'] != 0, denom / df_bs['total_assets'], 0)
    
    df_comp_sub = df_comp[['company_id', 'face_value']].copy() if 'face_value' in df_comp.columns else pd.DataFrame(columns=['company_id', 'face_value'])
    if not df_comp_sub.empty:
        df_comp_sub['face_value'] = pd.to_numeric(df_comp_sub['face_value'], errors='coerce')
        df_bs = df_bs.merge(df_comp_sub, on='company_id', how='left')
        shares = np.where(df_bs['face_value'] > 0, df_bs['equity_capital'] / df_bs['face_value'], np.nan)
        df_bs['book_value_per_share'] = np.where(shares > 0, denom / shares, np.nan)
        df_bs.drop(columns=['face_value'], inplace=True, errors='ignore')
    
    df_bs.to_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'), index=False)
    
    # 3. Clean Profit & Loss
    print("Cleaning profit and loss...")
    df_pl = pd.read_csv(os.path.join(RAW_DIR, 'profitandloss.csv'))
    df_pl.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    df_pl = clean_year_column(df_pl, 'year')
    
    num_cols_pl = ['sales', 'expenses', 'operating_profit', 'opm_percentage', 'other_income', 'interest', 'depreciation', 'profit_before_tax', 'tax_percentage', 'net_profit', 'eps', 'dividend_payout']
    for col in num_cols_pl:
        if col in df_pl.columns:
            df_pl[col] = pd.to_numeric(df_pl[col], errors='coerce').fillna(0)
            
    df_pl['net_profit_margin_pct'] = np.where(df_pl['sales'] != 0, (df_pl['net_profit'] / df_pl['sales']) * 100, 0)
    df_pl['expense_ratio_pct'] = np.where(df_pl['sales'] != 0, (df_pl['expenses'] / df_pl['sales']) * 100, 0)
    df_pl['interest_coverage'] = np.where(df_pl['interest'] != 0, df_pl['operating_profit'] / df_pl['interest'], df_pl['operating_profit'])
    
    df_pl.to_csv(os.path.join(CLEAN_DIR, 'profitandloss.csv'), index=False)
    
    # 4. Clean Cash Flow
    print("Cleaning cash flow...")
    df_cf = pd.read_csv(os.path.join(RAW_DIR, 'cashflow.csv'))
    df_cf.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    df_cf = clean_year_column(df_cf, 'year')
    
    num_cols_cf = ['operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']
    for col in num_cols_cf:
        if col in df_cf.columns:
            df_cf[col] = pd.to_numeric(df_cf[col], errors='coerce').fillna(0)
            
    df_cf['free_cash_flow'] = df_cf['operating_activity'] + df_cf['investing_activity']
    
    df_pl_sub = df_pl[['company_id', 'fiscal_year', 'net_profit']].dropna(subset=['fiscal_year'])
    df_cf = df_cf.merge(df_pl_sub, on=['company_id', 'fiscal_year'], how='left')
    df_cf['cash_conversion_ratio'] = np.where(df_cf['net_profit'].fillna(0) != 0, df_cf['operating_activity'] / df_cf['net_profit'], 0)
    df_cf.drop(columns=['net_profit'], inplace=True, errors='ignore')
    
    df_cf.to_csv(os.path.join(CLEAN_DIR, 'cashflow.csv'), index=False)
    
    # cross-table computations for BS
    df_bs = pd.read_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'))
    df_pl_sub2 = df_pl[['company_id', 'fiscal_year', 'sales', 'net_profit']].dropna(subset=['fiscal_year'])
    df_bs = df_bs.merge(df_pl_sub2, on=['company_id', 'fiscal_year'], how='left')
    
    df_bs['asset_turnover'] = np.where(df_bs['total_assets'] != 0, df_bs['sales'].fillna(0) / df_bs['total_assets'], 0)
    df_bs['return_on_assets'] = np.where(df_bs['total_assets'] != 0, (df_bs['net_profit'].fillna(0) / df_bs['total_assets']) * 100, 0)
    df_bs.drop(columns=['sales', 'net_profit'], inplace=True, errors='ignore')
    df_bs.to_csv(os.path.join(CLEAN_DIR, 'balancesheet.csv'), index=False)
    
    # 5. Clean Analysis
    print("Cleaning analysis...")
    df_an = pd.read_csv(os.path.join(RAW_DIR, 'analysis.csv'))
    df_an.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    
    records = []
    for _, row in df_an.iterrows():
        period = None
        for col in ['compounded_sales_growth', 'compounded_profit_growth', 'stock_price_cagr', 'roe']:
            if pd.notna(row.get(col)):
                p = extract_period(row[col])
                if p:
                    period = p
                    break
                    
        if not period:
            continue
            
        records.append({
            'company_id': row.get('company_id'),
            'period_label': period,
            'compounded_sales_growth_pct': extract_percent(row.get('compounded_sales_growth')),
            'compounded_profit_growth_pct': extract_percent(row.get('compounded_profit_growth')),
            'stock_price_cagr_pct': extract_percent(row.get('stock_price_cagr')),
            'roe_pct': extract_percent(row.get('roe'))
        })
        
    pd.DataFrame(records).to_csv(os.path.join(CLEAN_DIR, 'analysis.csv'), index=False)
    
    # 6. Generate Comprehensive Fundamental Pros & Cons for All Listed Companies
    print("Generating comprehensive pros & cons for all companies...")
    try:
        from etl.generate_pros_cons import generate_pros_cons_for_all
        generate_pros_cons_for_all()
    except Exception as e:
        print(f"Warning: Could not run automated pros/cons generator: {e}")
        # Fallback to raw pros and cons if generator fails
        df_pc = pd.read_csv(os.path.join(RAW_DIR, 'prosandcons.csv'))
        df_pc.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
        pc_records = []
        for _, row in df_pc.iterrows():
            comp = row.get('company_id')
            if pd.notna(row.get('pros')):
                pc_records.append({
                    'company_id': comp, 'is_pro': True, 'text': row['pros'],
                    'category': 'General', 'source': 'MANUAL', 'confidence': 1.0
                })
            if pd.notna(row.get('cons')):
                pc_records.append({
                    'company_id': comp, 'is_pro': False, 'text': row['cons'],
                    'category': 'General', 'source': 'MANUAL', 'confidence': 1.0
                })
        pd.DataFrame(pc_records).to_csv(os.path.join(CLEAN_DIR, 'prosandcons.csv'), index=False)
    
    # 7. Clean Documents
    print("Cleaning documents...")
    df_doc = pd.read_csv(os.path.join(RAW_DIR, 'documents.csv'))
    df_doc.replace({'NULL': np.nan, 'Null': np.nan}, inplace=True)
    df_doc = clean_year_column(df_doc, 'Year')
    df_doc.to_csv(os.path.join(CLEAN_DIR, 'documents.csv'), index=False)
    
    print("Cleaning and transformation completed.")

if __name__ == "__main__":
    main()
