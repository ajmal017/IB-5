import talib
import pandas as pd
from tqdm import tqdm


class technical_analysis:

    def __init__(self, df: pd.DataFrame, open: str, high: str, low: str,
                 close: str, volume: str):
        self.df = df
        self.high = df[high]
        self.open = df[open]
        self.low = df[low]
        self.close = df[close]
        self.volume = df[volume]

    def strategy_rsi_stochastic_ma(self):
        rsi = talib.RSI(self.close)
        slowk, slowd = talib.STOCH(self.high, self.low, self.close)
        ma = talib.MA(self.close)
        #kama = talib.KAMA(self.close)
        signal_ma = [0] * len(rsi)
        #signal_kama = [0] * len(rsi)
        for i in range(len(rsi)):
            if ((rsi[i] > 70) | (rsi[i] < 30)) & (
                    ((slowd[i] > 80) | (slowd[i] < 20)) & ((slowk[i] > 80) | (slowk[i] < 20))):
                if ma[i] > self.close[i]:
                    signal_ma[i] = 100
                if ma[i] < self.close[i]:
                    signal_ma[i] = -100
                '''
                if kama[i] > self.close[i]:
                    signal_kama[i] = 100
                if kama[i] < self.close[i]:
                    signal_kama[i] = -100
                '''
        return signal_ma#, signal_kama

    def strategy_cci_macd_sar(self):
        sar = talib.SAR(self.high,self.low)
        macd,macdsignal,macdhist = talib.MACD(self.close)
        cci = talib.CCI(self.high,self.low,self.close)
        signal = [0] * len(sar)

        for i in range(len(sar)):
            if sar[i] > self.close[i]:
                if -macdhist[i] > 0.9 * macd[i] and cci[i] < 100:

                    signal[i] = -100
            else:
                if macdhist[i] > macd[i] *0.9 and cci[i] > 100:
                    signal[i] = 100

        return signal




    def strategy_adx_di(self) -> list:
        adx = talib.DX(self.high, self.low, self.close)
        plus_di = talib.PLUS_DI(self.high, self.low, self.close)
        minus_di = talib.MINUS_DI(self.high, self.low, self.close)
        signal = []
        for i in range(len(adx)):
            if adx[i] < 25:
                signal.append(0)
            else:
                if plus_di[i] > minus_di[i]:
                    signal.append(100)
                else:
                    signal.append(-100)

        return signal

    def cycle_indicator(self) -> pd.DataFrame:
        df_cycle_indicator = pd.DataFrame()

        all_cycle_indicator_func = talib.__function_groups__['Cycle Indicators']
        # talib.get_functions()[:5]
        for func in tqdm(all_cycle_indicator_func):
            df_cycle_indicator[func] = pd.Series(getattr(talib, func)(self.close))

        return df_cycle_indicator

    def math_operator(self):
        all_math_operator_func = talib.__function_groups__['Math Operators']  # talib.get_functions()[5:16]

    def math_transform(self):
        all_math_func = talib.__function_groups__['Math Transform']  # talib.get_functions()[16:31]

    def momentum(self):
        all_momentum_func = talib.__function_groups__['Momentum Indicators']  # talib.get_functions()[31:61]

    def overlap(self):
        all_overlap_func = talib.__function_groups__['Overlap Studies']  # talib.get_functions()[61:78]

    def pattern_recgonition(self):
        all_pattern_recg_func = talib.__function_groups__['Pattern Recognition']  # talib.get_functions()[78:139]
        df = pd.DataFrame()
        for func in all_pattern_recg_func:
            df[func] = getattr(talib,func)(self.open,self.high,self.low,self.close)

        return df
    def price_transform(self):
        all_price_transform_func = talib.__function_groups__['Price Transform']  # talib.get_functions()[139:143]

    def statistical_function(self):
        all_stat_func = talib.__function_groups__['Statistic Functions']  # talib.get_functions()[143:152]

    def volatility(self):
        all_volaltility_func = talib.__function_groups__['Volatility Indicators']  # talib.get_functions()[152:155]

    def volume(df):
        all_volume_func = talib.__function_groups__['Volume Indicators']  # talib.get_functions()[155:158]


if __name__ == '__main__':
    df = pd.DataFrame(pd.read_csv('AAPL.csv'))
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'adj_Close', 'Volume']  # , 'Average', 'barCount']
    ta = technical_analysis(df, 'Open', 'High', 'Low', 'Close', 'Volume')
    df['signal'] = ta.strategy_adx_di()
    import matplotlib.pyplot as plt

    plt.show()
    print('')
