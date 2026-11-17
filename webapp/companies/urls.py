from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, ScoreViewSet, CashFlowViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'scores', ScoreViewSet, basename='score')
router.register(r'cashflow', CashFlowViewSet, basename='cashflow')

urlpatterns = [
    path('', include(router.urls)),
]
