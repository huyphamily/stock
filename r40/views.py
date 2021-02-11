from django.http import HttpResponse
from django.shortcuts import render
from r40.services import get_ratios, get_earning_companies
from common.util import convert_to_csv_format
from datetime import date
from re import match
import csv


def index(request):
    return HttpResponse("Placeholder")


def symbol(request, ticker):
    ratios = get_ratios(ticker)
    return HttpResponse(convert_to_csv_format(ratios))


def earning(request):
    report_date = request.GET.get("date")
    if report_date is None or not match("^\\d{4}-\\d{2}-\\d{2}$", report_date):
        report_date = date.today().strftime("%Y-%m-%d")
    companies = get_earning_companies(report_date)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="stock-{report_date}.csv"'

    writer = csv.writer(response)
    for i, company in enumerate(companies):
        if i == 0:
            writer.writerow([str(prop) for prop in company.keys()])

        writer.writerow([str(value) for value in company.values()])

    return response

    return HttpResponse(convert_to_csv_format(companies))

