from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import DimCompany, FactMLScores, FactCashFlow, FactProfitLoss, FactBalanceSheet, FactAnalysis
from .serializers import DimCompanySerializer, FactMLScoresSerializer, FactCashFlowSerializer
from django.db.models import Q

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all 100 companies with their health labels.
    """
    queryset = DimCompany.objects.all()
    serializer_class = DimCompanySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sector', 'symbol']

    @action(detail=True, methods=['get'])
    def charts(self, request, pk=None):
        company = self.get_object()
        
        # 1. Revenue & Profit Trend
        pl_data = FactProfitLoss.objects.filter(symbol=company).order_by('year_id')
        revenue_profit = {
            "years": [pl.year_id for pl in pl_data],
            "sales": [pl.sales for pl in pl_data],
            "net_profit": [pl.net_profit for pl in pl_data],
            "opm_pct": [pl.opm_pct for pl in pl_data]
        }
        
        # 2. Balance Sheet Composition
        bs_data = FactBalanceSheet.objects.filter(symbol=company).order_by('year_id')
        balance_sheet = {
            "years": [bs.year_id for bs in bs_data],
            "equity_reserves": [(bs.equity_capital or 0) + (bs.reserves or 0) for bs in bs_data],
            "borrowings": [bs.borrowings for bs in bs_data],
            "other_liabilities": [bs.other_liabilities for bs in bs_data]
        }
        
        # 3. Cash Flow Waterfall
        cf_data = FactCashFlow.objects.filter(symbol=company).order_by('year_id')
        cash_flow = {
            "years": [cf.year_id for cf in cf_data],
            "operating": [cf.operating_activity for cf in cf_data],
            "investing": [cf.investing_activity for cf in cf_data],
            "financing": [cf.financing_activity for cf in cf_data]
        }
        
        # 4. EPS & Dividend History
        eps_dividend = {
            "years": [pl.year_id for pl in pl_data],
            "eps": [pl.eps for pl in pl_data],
            "dividend_payout_pct": [pl.dividend_payout_pct for pl in pl_data]
        }
        
        # 5. Debt vs Equity
        debt_vs_equity = {
            "years": [bs.year_id for bs in bs_data],
            "borrowings": [bs.borrowings for bs in bs_data],
            "reserves": [bs.reserves for bs in bs_data]
        }
        
        # 6. CAGR Radar
        cagr_10y = FactAnalysis.objects.filter(symbol=company, period_label='10Y').first()
        cagr_5y = FactAnalysis.objects.filter(symbol=company, period_label='5Y').first()
        cagr_3y = FactAnalysis.objects.filter(symbol=company, period_label='3Y').first()
        
        cagr_radar = {
            "10Y": {
                "sales": cagr_10y.compounded_sales_growth_pct if cagr_10y else 0,
                "profit": cagr_10y.compounded_profit_growth_pct if cagr_10y else 0,
                "stock": cagr_10y.stock_price_cagr_pct if cagr_10y else 0,
                "roe": cagr_10y.roe_pct if cagr_10y else 0
            },
            "5Y": {
                "sales": cagr_5y.compounded_sales_growth_pct if cagr_5y else 0,
                "profit": cagr_5y.compounded_profit_growth_pct if cagr_5y else 0,
                "stock": cagr_5y.stock_price_cagr_pct if cagr_5y else 0,
                "roe": cagr_5y.roe_pct if cagr_5y else 0
            },
            "3Y": {
                "sales": cagr_3y.compounded_sales_growth_pct if cagr_3y else 0,
                "profit": cagr_3y.compounded_profit_growth_pct if cagr_3y else 0,
                "stock": cagr_3y.stock_price_cagr_pct if cagr_3y else 0,
                "roe": cagr_3y.roe_pct if cagr_3y else 0
            }
        }
        
        # 7. Margin Trend
        margin_trend = {
            "years": [pl.year_id for pl in pl_data],
            "opm_pct": [pl.opm_pct for pl in pl_data],
            "net_profit_margin_pct": [pl.net_profit_margin_pct for pl in pl_data]
        }
        
        # 8. Health Score Gauge
        score = FactMLScores.objects.filter(symbol=company).order_by('-computed_at').first()
        health_score = score.overall_score if score else 0
        
        return Response({
            "revenue_profit": revenue_profit,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
            "eps_dividend": eps_dividend,
            "debt_vs_equity": debt_vs_equity,
            "cagr_radar": cagr_radar,
            "margin_trend": margin_trend,
            "health_score": health_score
        })

class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FactMLScores.objects.all().order_by('-computed_at')
    serializer_class = FactMLScoresSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['symbol']

class CashFlowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FactCashFlow.objects.all().order_by('-year_id')
    serializer_class = FactCashFlowSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['symbol', 'year_id']
