from ib_insync import *
from scrapping.get_params import get_next_earning_release, get_next_working_day,get_next_friday
import pandas as pd
from tqdm import tqdm
from send_mail import send_mail
import datetime


def get_opt_param(stock,price_last):
    opt_param = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)[0]
    expirations = opt_param.expirations
    strikes = opt_param.strikes

    closest_expiration,next_expiration = expirations[0],expirations[1]
    closest_strike = min(strikes, key=lambda x: abs(x - price_last))
    next_strike = strikes[strikes.index(closest_strike) + 1]

    return closest_expiration,next_expiration,closest_strike,next_strike

def get_ticker_option_iv_and_spot(df):
    Ticker = []
    Last = []
    now_iv = []
    normal_iv = []
    expect_move = []

    for ticker, move in tqdm(zip(df['Symbol'], df['Expected Move - Next']), total=df.shape[0]):
        stock = Stock(ticker, 'SMART', 'USD')
        if ib.qualifyContracts(stock) == []:
            continue
        [stock] = ib.qualifyContracts(stock)
        [stock_mkt_data] = ib.reqTickers(stock)
        price_last = stock_mkt_data.last
        if ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId) == [] or price_last < 20:
            continue

        closest_expiration, next_expiration, closest_strike, next_strike = get_opt_param(stock,price_last)

        if closest_expiration != get_next_friday():continue

        option = Option(ticker, closest_expiration, closest_strike, 'C', 'SMART')

        if ib.qualifyContracts(option) == []:
            option = Option(ticker, closest_expiration, next_strike, 'C', 'SMART')
            if ib.qualifyContracts(option) == []:
                continue
        [option] = ib.qualifyContracts(option)

        '''
        while ib.qualifyContracts(option) == []:
            friday = get_next_friday(friday)
            option = Option(ticker, friday, round(price_last), 'C', 'SMART')
        '''

        [option_mkt_data] = ib.reqTickers(option)
        if option_mkt_data.askGreeks is None:continue
        opt_iv_ask = option_mkt_data.askGreeks.impliedVol

        opt_iv_bid = option_mkt_data.bidGreeks.impliedVol

        if opt_iv_bid is None or opt_iv_ask is None:
            continue
        opt_iv = (opt_iv_ask + opt_iv_bid) / 2

        next_option = Option(ticker, next_expiration, closest_strike, 'C', 'SMART')
        if ib.qualifyContracts(next_option) == []:
            next_option = Option(ticker, next_expiration, next_strike, 'C', 'SMART')
            if ib.qualifyContracts(next_option) == []:
                continue
        [next_option] = ib.qualifyContracts(next_option)

        '''
        while ib.qualifyContracts(next_option) == []:
            friday_next_month = get_next_friday(friday_next_month)
            next_option = Option(ticker,friday_next_month,round(price_last),'C','SMART')
        '''

        [nxt_option_mkt_data] = ib.reqTickers(next_option)
        if nxt_option_mkt_data.askGreeks is None:continue
        nxt_option_iv_ask = nxt_option_mkt_data.askGreeks.impliedVol
        nxt_option_iv_bid = nxt_option_mkt_data.bidGreeks.impliedVol
        if nxt_option_iv_bid is None or nxt_option_iv_ask is None:
            continue
        nxt_option_iv = (nxt_option_iv_ask + nxt_option_iv_bid) / 2
        Ticker.append(ticker)
        Last.append(price_last)
        now_iv.append(opt_iv)
        normal_iv.append(nxt_option_iv)
        expect_move.append(move)
    return pd.DataFrame(
        {'Ticker': Ticker, 'Last': Last, 'expect_move': expect_move, 'OverValued_IV': now_iv, 'Normal_iv': normal_iv})


if __name__ == '__main__':
    ib = IB()
    ib.connect(host='127.0.0.1', port=7496, clientId=999)
    '''
    from tqdm import tqdm
    import datetime
    fut = Future('ES', '201912', 'GLOBEX')
    stock = Stock('FDX','SMART','USD')
    df_all = pd.DataFrame()
    for time in tqdm(pd.date_range('20190501','20191129',freq=pd.offsets.BDay())):

        bars = ib.reqHistoricalData(stock,
                                    endDateTime=time,#datetime.date(2019, 11, 29),
                                    durationStr='1 D',
                                    barSizeSetting='10 mins',
                                    whatToShow='TRADES',
                                    useRTH=True,
                                    formatDate=1)
        df = util.df(bars)
        df_all = df_all.append(df)

    df_all.to_csv('data.csv',index = False)
    '''
    # list_earning_release = get_next_earning_release()
    date_input_1 = input('please enter first date(format yyyy/mm/dd) :')
    date_input_2 = input('please enter second date(format yyyy/mm/dd) :')

    date_input_1 = datetime.datetime.strptime(date_input_1,'%Y/%m/%d')
    date_input_2 = datetime.datetime.strptime(date_input_2,'%Y/%m/%d')
    df = pd.read_csv('FutureEarningsResults.csv')
    df['Date - Next'] = pd.to_datetime(df['Date - Next'])
    df_today = df[df['Date - Next'] == date_input_1]#datetime.datetime.today().date() ]
    df_today = df_today[df_today['Time - Next'] == 'AMC']
    df_tomorrow = df[df['Date - Next'] == date_input_2]#get_next_working_day().date() ]
    df_tomorrow = df_tomorrow[df_tomorrow['Time - Next'] == 'BMO']

    print('')

    df_earnings_today = get_ticker_option_iv_and_spot(df_today )

    df_earnings_tomorrow = get_ticker_option_iv_and_spot(df_tomorrow)

    df_earning = df_earnings_today.append(df_earnings_tomorrow)
    df_earning.to_csv('all.csv', index=False)
    # ib.disconnect()

    print('Data is generated')

    df = df_earning.copy()
    df.reset_index(inplace=True)

    df['difference'] = df['OverValued_IV'] - df['Normal_iv']

    df_new = df.sort_values(by='difference', ascending=False)
    df_new.dropna(how='any', inplace=True, axis=0)
    df_new['difference'] = df_new['difference'].apply(lambda x: str(round(x * 100)) + '%')
    df_new['expect_move'] = df_new['expect_move'].apply(lambda x: str(round(x * 100)) + '%')
    subject = 'Stocks overvalued (spot > 20)'
    content = df_new.style.render().replace("\n", "")
    send_mail(subject, content)
