from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from companies.models import DimCompany, FactMLScores, FactCashFlow, FactBalanceSheet, FactProfitLoss, FactAnalysis, FactProsCons

def index(request):
    scores = FactMLScores.objects.select_related('symbol').all().order_by('-overall_score')
    return render(request, 'dashboard/index.html', {'scores': scores})

def company_list(request):
    return render(request, 'dashboard/company_list.html')

def company_detail(request, symbol):
    company = get_object_or_404(DimCompany, symbol=symbol)
    latest_score = FactMLScores.objects.filter(symbol=company).order_by('-computed_at').first()
    pros = FactProsCons.objects.filter(symbol=company, is_pro=True)
    cons = FactProsCons.objects.filter(symbol=company, is_pro=False)
    # The charts will fetch data via AJAX, but we pass basic info
    return render(request, 'dashboard/company_detail.html', {
        'company': company, 
        'score': latest_score,
        'pros': pros,
        'cons': cons
    })

def compare(request):
    return render(request, 'dashboard/compare.html')

def screener(request):
    return render(request, 'dashboard/screener.html')

def sector_detail(request, name):
    companies = DimCompany.objects.filter(sector__iexact=name)
    return render(request, 'dashboard/sector_detail.html', {'sector_name': name, 'companies': companies})
