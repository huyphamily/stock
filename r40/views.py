from django.http import HttpResponse
from django.shortcuts import render
from r40.services import get_ratios, get_earning_companies
from common.util import convert_to_csv_format


def index(request):
    return HttpResponse("Placeholder")


def symbol(request, ticker):
    ratios = get_ratios(ticker)
    return HttpResponse(convert_to_csv_format(ratios))


def earning(request):
    report_date = request.GET.get("date")
    companies = get_earning_companies(report_date)
    return HttpResponse(convert_to_csv_format(companies))

