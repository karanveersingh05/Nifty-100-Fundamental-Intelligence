from django.urls import path
from .views import (
    FullCompanyDataView,
    BulkFinancialsView,
    ScreenerAPIView,
    ScoresAPIView,
    APIKeyManageView,
    WebhookManageView,
)

urlpatterns = [
    path('companies/<str:symbol>/full/', FullCompanyDataView.as_view(), name='partner_company_full'),
    path('bulk-financials/', BulkFinancialsView.as_view(), name='partner_bulk_financials'),
    path('screener/', ScreenerAPIView.as_view(), name='partner_screener'),
    path('scores/', ScoresAPIView.as_view(), name='partner_scores'),
    path('keys/', APIKeyManageView.as_view(), name='partner_keys'),
    path('webhooks/', WebhookManageView.as_view(), name='partner_webhooks'),
]
