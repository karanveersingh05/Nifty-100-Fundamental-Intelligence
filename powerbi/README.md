# Power BI Dashboards

This directory contains the 7 Power BI dashboard placeholders required for Phase 2.

## Dashboards Created
1. `01_executive_overview.pbix`
2. `02_company_deep_dive.pbix`
3. `03_sector_comparison.pbix`
4. `04_health_scorecard.pbix`
5. `05_growth_analytics.pbix`
6. `06_debt_leverage.pbix`
7. `07_dividend_returns.pbix`

## Connection Instructions
1. Open Power BI Desktop -> Get Data -> PostgreSQL Database
2. Enter server: `localhost:5432`, database: `bluestock_dw`
3. Import all `dim_*` and `fact_*` tables.

## Data Model Relationships
Set the following relationships in the Power BI model view (all Many-to-One):
- `fact_profit_loss[symbol]` -> `dim_company[symbol]`
- `fact_profit_loss[year_id]` -> `dim_year[year_id]`
- `fact_balance_sheet[symbol]` -> `dim_company[symbol]`
- `fact_balance_sheet[year_id]` -> `dim_year[year_id]`
- `fact_cash_flow[symbol]` -> `dim_company[symbol]`
- `fact_cash_flow[year_id]` -> `dim_year[year_id]`
- `fact_analysis[symbol]` -> `dim_company[symbol]`
- `fact_ml_scores[symbol]` -> `dim_company[symbol]`
- `fact_pros_cons[symbol]` -> `dim_company[symbol]`
- `dim_company[sector]` -> `dim_sector[sector_name]`

## Required DAX Measures Examples

**Executive Overview:**
- `Total Companies` = COUNT(dim_company[symbol])
- `Average ROE (All Companies)` = AVERAGE(fact_profit_loss[roe_pct_3y])
- `Companies with Excellent Health` = COUNTROWS(FILTER(fact_ml_scores, [score] >= 85))
- `Companies with Weak/Poor Health` = COUNTROWS(FILTER(fact_ml_scores, [score] < 50))

**Company Deep Dive:**
- `Company Name` = SELECTEDVALUE(dim_company[company_name])
- `Health Label` = SELECTEDVALUE(fact_ml_scores[health_label])

**Growth & Analytics:**
- `Consistent Growers` = IF(COUNTROWS(FILTER(fact_profit_loss, [sales_growth_yoy] > 0)) >= 5, 1, 0)
