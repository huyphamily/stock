import fmpsdk
import environ


env = environ.Env()
environ.Env.read_env()
fmp_api_key = env("FMP_API_KEY", default="fmpapikey")


def get_ratios(symbol, limit=50):
    # fetch quarterly reports from fmp
    quarterly = fmpsdk.income_statement(apikey=fmp_api_key,
                                        symbol=symbol.upper(),
                                        period='quarter',
                                        limit=limit)

    quarterly_counts = len(quarterly)

    # sort quarterly reports by date
    sorted(quarterly, key=lambda q: q['date'])

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
            'Date': curr_qr.get('date'),
            'Rule 40': annual_qr_growth + ebitda_ratio,
            'Ebita Ratio': ebitda_ratio,
            'Annual Growth': annual_qr_growth,
        }
        ratios.append(data)

    ratios.reverse()
    return ratios
