from django.db import models

# using managed=False here because I don't want a Django migration accidentally nuking our warehouse

class DimCompany(models.Model):
    symbol = models.CharField(max_length=50, primary_key=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    sub_sector = models.CharField(max_length=100, null=True, blank=True)
    company_logo = models.CharField(max_length=255, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    nse_url = models.CharField(max_length=255, null=True, blank=True)
    bse_url = models.CharField(max_length=255, null=True, blank=True)
    face_value = models.FloatField(null=True, blank=True)
    book_value = models.FloatField(null=True, blank=True)
    about_company = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'dim_company'

class FactMLScores(models.Model):
    # we're mapping the composite PK by designating the ForeignKey as primary_key for Django
    symbol = models.OneToOneField(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol', primary_key=True)
    computed_at = models.DateTimeField()
    overall_score = models.FloatField(null=True, blank=True)
    profitability_score = models.FloatField(null=True, blank=True)
    growth_score = models.FloatField(null=True, blank=True)
    leverage_score = models.FloatField(null=True, blank=True)
    cashflow_score = models.FloatField(null=True, blank=True)
    dividend_score = models.FloatField(null=True, blank=True)
    trend_score = models.FloatField(null=True, blank=True)
    health_label = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_ml_scores'

class FactProfitLoss(models.Model):
    symbol = models.ForeignKey(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol', primary_key=True)
    year_id = models.IntegerField()
    sales = models.FloatField(null=True, blank=True)
    expenses = models.FloatField(null=True, blank=True)
    operating_profit = models.FloatField(null=True, blank=True)
    opm_pct = models.FloatField(null=True, blank=True)
    other_income = models.FloatField(null=True, blank=True)
    interest = models.FloatField(null=True, blank=True)
    depreciation = models.FloatField(null=True, blank=True)
    profit_before_tax = models.FloatField(null=True, blank=True)
    tax_pct = models.FloatField(null=True, blank=True)
    net_profit = models.FloatField(null=True, blank=True)
    eps = models.FloatField(null=True, blank=True)
    dividend_payout_pct = models.FloatField(null=True, blank=True)
    net_profit_margin_pct = models.FloatField(null=True, blank=True)
    expense_ratio_pct = models.FloatField(null=True, blank=True)
    interest_coverage = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_profit_loss'

class FactBalanceSheet(models.Model):
    symbol = models.ForeignKey(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol', primary_key=True)
    year_id = models.IntegerField()
    equity_capital = models.FloatField(null=True, blank=True)
    reserves = models.FloatField(null=True, blank=True)
    borrowings = models.FloatField(null=True, blank=True)
    other_liabilities = models.FloatField(null=True, blank=True)
    total_liabilities = models.FloatField(null=True, blank=True)
    fixed_assets = models.FloatField(null=True, blank=True)
    cwip = models.FloatField(null=True, blank=True)
    investments = models.FloatField(null=True, blank=True)
    other_assets = models.FloatField(null=True, blank=True)
    total_assets = models.FloatField(null=True, blank=True)
    debt_to_equity = models.FloatField(null=True, blank=True)
    equity_ratio = models.FloatField(null=True, blank=True)
    book_value_per_share = models.FloatField(null=True, blank=True)
    asset_turnover = models.FloatField(null=True, blank=True)
    return_on_assets = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_balance_sheet'

class FactCashFlow(models.Model):
    symbol = models.ForeignKey(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol', primary_key=True)
    year_id = models.IntegerField()
    operating_activity = models.FloatField(null=True, blank=True)
    investing_activity = models.FloatField(null=True, blank=True)
    financing_activity = models.FloatField(null=True, blank=True)
    net_cash_flow = models.FloatField(null=True, blank=True)
    free_cash_flow = models.FloatField(null=True, blank=True)
    cash_conversion_ratio = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_cash_flow'

class FactAnalysis(models.Model):
    symbol = models.ForeignKey(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol', primary_key=True)
    period_label = models.CharField(max_length=50)
    compounded_sales_growth_pct = models.FloatField(null=True, blank=True)
    compounded_profit_growth_pct = models.FloatField(null=True, blank=True)
    stock_price_cagr_pct = models.FloatField(null=True, blank=True)
    roe_pct = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_analysis'

class FactProsCons(models.Model):
    id = models.AutoField(primary_key=True)
    symbol = models.ForeignKey(DimCompany, on_delete=models.DO_NOTHING, db_column='symbol')
    is_pro = models.BooleanField(null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'fact_pros_cons'
