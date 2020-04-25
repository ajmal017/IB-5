from datetime import datetime
import calendar
import datetime
import requests
import pandas as pd
from yahoo_earnings_calendar import YahooEarningsCalendar
apikey = 'AHZS0AEZ9I63G6Y0'

'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=demo'

FUNCTION = {'stock_daily_adjusted': 'TIME_SERIES_DAILY_ADJUSTED', 'stock_daily': 'TIME_SERIES_DAILY',
            'stock_intraday': 'TIME_SERIES_INTRADAY', 'stock_weekly': 'TIME_SERIES_WEEKLY',
            'stock_weekly_adjusted': 'TIME_SERIES_MONTHLY_ADJUSTED', 'stock_monthly': 'TIME_SERIES_MONTHLY',
            'stock_monthly_adjusted': 'TIME_SERIES_MONTHLY_ADJUSTED',
            'forex_intraday': 'FX_INTRADAY'}
INTERVAL = {'1min': '1min', '5min': '5min', '15min': '15min', '30min': '30min', '60min': '60min'}


def get_next_working_day():
    today = datetime.datetime.today()
    if today.isoweekday() == 5:
        next_working_day = today + datetime.timedelta(3)
    else:
        next_working_day = today + datetime.timedelta(1)
    return  next_working_day

def get_next_friday(date= ''):
    if date == '':
        date = datetime.datetime.today()
        day = date.isoweekday()
        date += datetime.timedelta(5 - day)
    else:
        date = datetime.datetime.strptime(date,'%Y%m%d')
        day = date.isoweekday()
        if day ==5 :
            date += datetime.timedelta(7)
        else:
            date += datetime.timedelta(5 - day)
    return date.strftime('%Y%m%d')


def get_next_month(date):
    start_date = datetime.datetime.strptime(date,'%Y%m%d')
    days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + datetime.timedelta(days=days_in_month)
    return end_date.strftime('%Y%m%d')

def get_next_earning_release() -> list:
    date_from = datetime.datetime.today()
    date_to = get_next_working_day()
    yec = YahooEarningsCalendar()
    all_ticker = list()
    today_earnings = yec.earnings_on(date_from)
    tomorrow_earnings = yec.earnings_on(date_to)

    for stock1,stock2 in zip(today_earnings,tomorrow_earnings):
        if stock1['startdatetimetype'] == 'AMC':
            all_ticker.append(stock1['ticker'])
        if stock2['startdatetimetype'] == 'BMO':
            all_ticker.append(stock2['ticker'])

    return all_ticker


def generate_url(case, function, apikey, symbol_1, interval=None, symbol_2=None):
    url_begin = 'https://www.alphavantage.co/query'
    url_supplement = ''
    if case == 'stock':
        # url_begin = 'https://www.alphavantage.co/query?function='
        if interval == None:
            url_supplement = '?function=' + FUNCTION[function] + '&symbol=' + symbol_1 + '&apikey=' + apikey
        else:
            url_supplement = '?function=' + FUNCTION[
                function] + '&symbol=' + symbol_1 + '&interval=' + interval + '&apikey=' + apikey

    elif case == 'forex':
        # url_begin = 'https://www.alphavantage.co/query?'
        url_supplement = '?function=' + FUNCTION[
            function] + '&from_symbol=' + symbol_1 + '&to_symbol=' + symbol_2 + '&interval=' + interval + '&apikey=' + apikey

    return url_begin + url_supplement


def serach_symbol(key_words):
    url_begin = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'
    url_supplement = '&keywords=' + str(key_words).upper() + '&apikey=' + apikey

    return url_begin + url_supplement


'''
api_headers = {
    "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com",
    "X-RapidAPI-Key": "7d6fe46a8emsh013e50418e263adp15002ajsn9d6e31e35079"}

dict_region = {'AU': 'AU', 'CA': 'CA', 'FR': 'FR', 'DE': 'DE', 'HK': 'HK', 'US': 'US', 'IT': 'IT', 'ES': 'ES', 'GB': 'GB',
          'IN': 'IN'}

dict_events = {'DIV': 'div', 'SPLIT': 'split', 'EARN': 'earn'}

dict_interval = {'daily': '1d', '5-days': '5d', 'monthly': '1mo', '3-months': '3mo', 'half-year': '6mo', 'yearly': '1y',
            '2-years': '2y', '5-years': '5y', 'MAX': 'max'}


def generate_url(region, symbol, from_time, to_time, events, interval):
    url_1 = 'https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/get-histories?region='

    dt_from = time.mktime(datetime.strptime(from_time, '%Y-%m-%d').timetuple())
    dt_to = time.mktime(datetime.strptime(to_time, '%Y-%m-%d').timetuple())

    string_time = '&from=' + str(dt_from)[:-2] + '&to=' + str(dt_to)[:-2]

    url_2 = '&lang=en&symbol='

    string_supplement = '&events=' + dict_events[events] + '&interval=' + dict_interval[interval]

    return url_1 + dict_region[region]  + url_2+symbol+string_time+string_supplement
'''
