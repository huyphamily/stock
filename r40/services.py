import fmpsdk
from datetime import date, datetime
from re import match
from stock.env import FMP_API_KEY


INDUSTRY_ALLOW_LIST = {"Software Application", "Software Infrastructure", "Internet Content & Information"}
FILLING_NAME_8K = "8-K"


def get_earning_companies(report_date):
    if report_date is None or not match("^\\d{4}-\\d{2}-\\d{2}$", report_date):
        report_date = date.today().strftime("%Y-%m-%d")

    companies = fmpsdk.earning_calendar(apikey=FMP_API_KEY, from_date=report_date, to_date=report_date)
    filtered_companies = []

    for company in companies:
        cur_company_symbol = company.get("symbol")
        company_profile = fmpsdk.company_profile(apikey=FMP_API_KEY, symbol=cur_company_symbol)
        if len(company_profile) > 0 and company_profile[0].get("industry") in INDUSTRY_ALLOW_LIST:
            company_profile_obj = company_profile[0]
            # r40 score
            data = get_latest_rule40(cur_company_symbol)
            if data is None:
                data = {
                    "Ticker": cur_company_symbol.upper(),
                    "Date": "N/A",
                    "Rule 40": "N/A",
                    "Ebita Ratio": "N/A",
                    "Annual Growth": "N/A",
                }

            # Other info
            data["Country"] = company_profile_obj.get("country")
            data["Exchange"] = company_profile_obj.get("exchangeShortName")
            data["Industry"] = company_profile_obj.get("industry")
            data["Sector"] = company_profile_obj.get("sector")

            # sec filing
            filings = fmpsdk.sec_filings(apikey=FMP_API_KEY, symbol=cur_company_symbol, limit=10)

            data["8K File"] = "N/A"
            data["8K Date"] = "N/A"
            for filing in filings:
                if filing.get("type") == FILLING_NAME_8K:
                    data["8K File"] = filing.get("finalLink")
                    data["8K Date"] = datetime.strptime(filing.get("fillingDate"), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                    break

            data["SEC Link"] = "N/A" if len(filings) == 0\
                else "https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + filings[0].get("cik")

            filtered_companies.append(data)

    return filtered_companies


def get_ratios(symbol, limit=50):
    # fetch quarterly reports from fmp
    quarterly = fmpsdk.income_statement(apikey=FMP_API_KEY,
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
    quarterlies = fmpsdk.income_statement(apikey=FMP_API_KEY,
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
