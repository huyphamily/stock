import fmpsdk
import environ
from datetime import date, datetime
from re import match


env = environ.Env()
environ.Env.read_env("stock/.env")
fmp_api_key = env("FMP_API_KEY", default="fmpapikey")

INDUSTRY_ALLOW_LIST = {'Software Application', 'Software Infrastructure', 'Internet Content & Information'}


def get_earning_companies(report_date):
    if report_date is None or not match("^\\d{4}-\\d{2}-\\d{2}$", report_date):
        report_date = date.today().strftime("%Y-%m-%d")

    companies = fmpsdk.earning_calendar(apikey=fmp_api_key, from_date=report_date, to_date=report_date)
    filtered_companies = []

    for company in companies:
        cur_company_symbol = company.get("symbol")
        company_profile = fmpsdk.company_profile(apikey=fmp_api_key, symbol=cur_company_symbol)
        if len(company_profile) > 0 and company_profile[0].get("industry") in INDUSTRY_ALLOW_LIST:
            company_profile_obj = company_profile[0]
            data = get_latest_rule40(cur_company_symbol)

            if data is None:
                continue

            data["Country"] = company_profile_obj.get("country")
            data["Exchange"] = company_profile_obj.get("exchangeShortName")
            data["Industry"] = company_profile_obj.get("industry")
            data["Sector"] = company_profile_obj.get("sector")
            filtered_companies.append(data)

    return filtered_companies


def get_ratios(symbol, limit=50):
    # fetch quarterly reports from fmp
    quarterly = fmpsdk.income_statement(apikey=fmp_api_key,
                                        symbol=symbol.upper(),
                                        period='quarter',
                                        limit=limit)

    quarterly_counts = len(quarterly)

    # sort quarterly reports by date
    sorted(quarterly, key=lambda q: q['fillingDate'])

    # calculate rule40 for each quarter
    ratios = []
    for i in range(0, quarterly_counts - 4):
        curr_qr = quarterly[i]
        past_year = quarterly[i + 4]

        if not curr_qr.get('ebitda') or not curr_qr.get('revenue'):
            continue

        if curr_qr.get('revenue') == 0 or past_year.get('revenue') == 0:
            continue

        annual_qr_growth = (curr_qr.get('revenue') - past_year.get('revenue')) / past_year.get('revenue')
        ebitda_ratio = curr_qr.get('ebitda')/curr_qr.get('revenue')

        data = {
            'Ticker': symbol.upper(),
            'Date': curr_qr.get('fillingDate'),
            'Rule 40': annual_qr_growth + ebitda_ratio,
            'Ebita Ratio': ebitda_ratio,
            'Annual Growth': annual_qr_growth,
        }
        ratios.append(data)

    ratios.reverse()
    return ratios


def get_latest_rule40(ticker):
    ticker = ticker.upper()
    quarterlies = fmpsdk.income_statement(apikey=fmp_api_key,
                                          symbol=ticker,
                                          period='quarter',
                                          limit=5)

    if len(quarterlies) < 5:
        return None

    try:
        curr_qr = quarterlies[0]
        past_year = quarterlies[4]

        # shitty date screener
        if curr_qr.get('fillingDate').startswith('2020') or curr_qr.get('fillingDate').startswith('2021'):
            annual_qr_growth = (curr_qr.get('revenue') - past_year.get('revenue')) / past_year.get('revenue')
            ebitda_ratio = curr_qr.get('ebitda') / curr_qr.get('revenue')

            data = {
                'Ticker': ticker,
                'Date': curr_qr.get('fillingDate'),
                'Rule 40': annual_qr_growth + ebitda_ratio,
                'Ebita Ratio': ebitda_ratio,
                'Annual Growth': annual_qr_growth,
            }

            if data:
                return data
    except ZeroDivisionError:
        return None
    return None
