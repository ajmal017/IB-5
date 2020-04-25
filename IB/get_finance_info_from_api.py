import requests
from scrapping.get_params import generate_url, apikey, serach_symbol  # ,api_headers
import pandas as pd
import matplotlib.pyplot as plt


# url = generate_url('US','AAPL','2019-01-01','2019-07-01','DIV','daily')

def get_symbol(input):
    symbol_search_url = serach_symbol(input)
    r = requests.get(symbol_search_url)
    dict_all = r.json()
    return pd.DataFrame(dict_all['bestMatches'])


def get_forex_info(ccy_in, ccy_out, function, interval):
    forex_url = generate_url('forex', str(function).upper(), apikey, str(ccy_in).strip().upper(), interval, str(
        ccy_out).strip().upper())  # generate_url('forex','forex_intraday',apikey,'EUR','5min','GBP')
    r = requests.get(forex_url)
    dict_all = r.json()


def get_stock_info(function, name, interval):
    url = generate_url('stock', function.strip(), apikey, name.strip().upper(),
                       interval=interval)  # generate_url('stock', 'stock_intraday', apikey, 'NFLX', interval='5min')
    r = requests.get(url)
    dict_all = r.json()
    # dict_info_time_series_daily = dict_all['Time Series (Daily)']
    try:
        df_final = pd.DataFrame(dict_all[list(dict_all.keys())[1]]).T
        return df_final.iloc[::-1]
    except Exception as e:
        print(name, function, interval)


# symbol_search_json = serach_symbol('netflix')


def get_stock_list_percent_change(stock_last_close, df):
    stock_print = dict()
    for stock_high_vol, stock_low_vol in zip(df['high_vol'], df['low_vol']):

        stock_high_vol_current_price = \
            get_stock_info(function='stock_intraday', name=stock_high_vol, interval='1min')['4. close'][0]

        stock_low_vol_current_price = \
            get_stock_info(function='stock_intraday', name=stock_low_vol, interval='1min')['4. close'][0]

        stock_high_vol_last_price = stock_last_close[stock_high_vol]
        stock_low_vol_last_price = stock_last_close[stock_low_vol]
        high_vol_pct_change = (float(stock_high_vol_current_price) - float(stock_high_vol_last_price)) / (
            float(stock_high_vol_last_price))
        low_vol_pct_change = (float(stock_low_vol_current_price) - float(stock_low_vol_last_price)) / (
            float(stock_low_vol_last_price))
        if abs(high_vol_pct_change) >= 0.03:
            stock_print[stock_high_vol] = high_vol_pct_change
        if abs(low_vol_pct_change) >= 0.02:
            stock_print[stock_low_vol] = low_vol_pct_change

    return stock_print


def get_stock_pct_change_history(name, change):
    function = 'stock_daily'
    df_info = get_stock_info(function, name, None).astype(float).rename({'4. close': 'CLOSE'}, axis=1)
    if change == '':
        change = 0
    else:
        change = float(change)
    df_pct_change = df_info.pct_change().rename({'CLOSE': 'CLOSE_Pct'}, axis=1)
    df_close = pd.DataFrame([df_info['CLOSE'], df_pct_change['CLOSE_Pct']]).T
    df_close['CLOSE_Pct'] *= 100
    if change > 0:
        df_reserve = df_close[df_close['CLOSE_Pct'] >= change]
    else:
        df_reserve = df_close[df_close['CLOSE_Pct'] <= change]
    df_show = pd.DataFrame()

    for date in df_reserve.index:
        df_temp = df_close.iloc[df_close.index.get_loc(date) - 1: df_close.index.get_loc(date) + 2]
        df_show = df_show.append(df_temp)
    df_show.drop_duplicates(inplace=True)
    df_show['CLOSE_Pct'] = df_show['CLOSE_Pct'].apply(lambda x: str(round(x, 2)) + '%')

    return df_show, df_reserve

# to_plot = pd.Series([float(dict_info_time_series_daily[x]['4. close']) for x in dict_info_time_series_daily.keys()])
# to_plot.plot()
# plt.show()
# get_stock_list_percent_change()
