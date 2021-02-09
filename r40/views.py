from django.http import HttpResponse
from django.shortcuts import render
from r40.services import get_ratios


def index(request):
    return HttpResponse("Placeholder")


def symbol(request, ticker):
    ratios = get_ratios(ticker)

    output = ''

    for r in ratios:
        output += ",".join(str(r) for r in r.values())
        output += '\n'

    return HttpResponse(ratios)
