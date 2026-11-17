from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DimCompany(Base):
    __tablename__ = 'dim_company'
    symbol = Column(String(50), primary_key=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    sub_sector = Column(String(100))
    company_logo = Column(String(255))
    website = Column(String(255))
    nse_url = Column(String(255))
    bse_url = Column(String(255))
    face_value = Column(Float)
    book_value = Column(Float)
    about_company = Column(Text)

class DimYear(Base):
    __tablename__ = 'dim_year'
    year_id = Column(Integer, primary_key=True)
    year_label = Column(String(50))
    fiscal_year = Column(Integer)
    quarter = Column(String(10))
    is_ttm = Column(Boolean)
    is_half_year = Column(Boolean)
    sort_order = Column(Integer)

class DimSector(Base):
    __tablename__ = 'dim_sector'
    sector_id = Column(Integer, primary_key=True, autoincrement=True)
    sector_name = Column(String(100), unique=True)
    sector_code = Column(String(50))
    description = Column(Text)

class DimHealthLabel(Base):
    __tablename__ = 'dim_health_label'
    label_id = Column(Integer, primary_key=True, autoincrement=True)
    label_name = Column(String(50), unique=True)
    min_score = Column(Float)
    max_score = Column(Float)
    color_hex = Column(String(10))

class FactProfitLoss(Base):
    __tablename__ = 'fact_profit_loss'
    symbol = Column(String(50), ForeignKey('dim_company.symbol'), primary_key=True)
    year_id = Column(Integer, ForeignKey('dim_year.year_id'), primary_key=True)
    sales = Column(Float)
    expenses = Column(Float)
    operating_profit = Column(Float)
    opm_pct = Column(Float)
    other_income = Column(Float)
    interest = Column(Float)
    depreciation = Column(Float)
    profit_before_tax = Column(Float)
    tax_pct = Column(Float)
    net_profit = Column(Float)
    eps = Column(Float)
    dividend_payout_pct = Column(Float)
    net_profit_margin_pct = Column(Float)
    expense_ratio_pct = Column(Float)
    interest_coverage = Column(Float)

class FactBalanceSheet(Base):
    __tablename__ = 'fact_balance_sheet'
    symbol = Column(String(50), ForeignKey('dim_company.symbol'), primary_key=True)
    year_id = Column(Integer, ForeignKey('dim_year.year_id'), primary_key=True)
    equity_capital = Column(Float)
    reserves = Column(Float)
    borrowings = Column(Float)
    other_liabilities = Column(Float)
    total_liabilities = Column(Float)
    fixed_assets = Column(Float)
    cwip = Column(Float)
    investments = Column(Float)
    other_assets = Column(Float)
    total_assets = Column(Float)
    debt_to_equity = Column(Float)
    equity_ratio = Column(Float)
    book_value_per_share = Column(Float)
    asset_turnover = Column(Float)
    return_on_assets = Column(Float)

class FactCashFlow(Base):
    __tablename__ = 'fact_cash_flow'
    symbol = Column(String(50), ForeignKey('dim_company.symbol'), primary_key=True)
    year_id = Column(Integer, ForeignKey('dim_year.year_id'), primary_key=True)
    operating_activity = Column(Float)
    investing_activity = Column(Float)
    financing_activity = Column(Float)
    net_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    cash_conversion_ratio = Column(Float)

class FactAnalysis(Base):
    __tablename__ = 'fact_analysis'
    symbol = Column(String(50), ForeignKey('dim_company.symbol'), primary_key=True)
    period_label = Column(String(50), primary_key=True)
    compounded_sales_growth_pct = Column(Float)
    compounded_profit_growth_pct = Column(Float)
    stock_price_cagr_pct = Column(Float)
    roe_pct = Column(Float)

class FactMLScores(Base):
    __tablename__ = 'fact_ml_scores'
    symbol = Column(String(50), ForeignKey('dim_company.symbol'), primary_key=True)
    computed_at = Column(DateTime, primary_key=True)
    overall_score = Column(Float)
    profitability_score = Column(Float)
    growth_score = Column(Float)
    leverage_score = Column(Float)
    cashflow_score = Column(Float)
    dividend_score = Column(Float)
    trend_score = Column(Float)
    health_label = Column(String(50))

class FactProsCons(Base):
    __tablename__ = 'fact_pros_cons'
    # using a surrogate key here because there can be multiple text entries per company
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), ForeignKey('dim_company.symbol'))
    is_pro = Column(Boolean)
    category = Column(String(100))
    text = Column(Text)
    source = Column(String(50))
    confidence = Column(Float)
    generated_at = Column(DateTime)
