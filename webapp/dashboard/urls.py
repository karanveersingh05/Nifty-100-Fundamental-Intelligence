from django.urls import path
from .views import index, company_list, company_detail, compare, screener, sector_detail

urlpatterns = [
    path('', index, name='index'),
    path('companies/', company_list, name='company_list'),
    path('company/<str:symbol>/', company_detail, name='company_detail'),
    path('compare/', compare, name='compare'),
    path('screener/', screener, name='screener'),
    path('sector/<str:name>/', sector_detail, name='sector_detail'),
]
