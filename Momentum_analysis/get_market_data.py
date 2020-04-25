from tqdm import tqdm
import datetime
from ib_insync import *
import pandas as pd

ib = IB()
ib.connect(host='127.0.0.1', port=7496, clientId=999)
#fut = Future('ES', '201912', 'GLOBEX')
stock = Stock('AAPL', 'SMART', 'USD')
df_all = pd.DataFrame()
#for time in tqdm(pd.date_range('20190501', '20191129', freq=pd.offsets.BDay())):
bars = ib.reqHistoricalData(stock,
                            endDateTime=datetime.datetime.today(),
                            durationStr='5 Y',
                            barSizeSetting='1 day',
                            whatToShow='TRADES',
                            useRTH=True,
                            formatDate=1)
df = util.df(bars)
df_all = df_all.append(df)

df_all.to_csv('AAPL_1Year_daily.csv', index=False)
print('done')