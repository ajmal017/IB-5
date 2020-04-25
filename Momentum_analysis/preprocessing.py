import pandas as pd
from parameters import train_file


class preprocessing:
    def __init__(self):
        self.df_data = pd.read_csv(train_file)

    def _transform_func_1(self,x,param = 100):
        if x > param:
            return 1
        elif x< - param:
            return 0
        else:
            return 1/200 * x +0.5

    def _transform_func_2(self,x):
        if x <= 0 :
            temp = 1-x
        else:
            temp  = 1/(1+x)
        return 1/(1+temp)

    def _transform_func_3(self,x,param = 100):
        if x > param:
            return 1
        elif x < -param:
            return 0
        elif x < 0 :
            return -1/2/1e4*x*x+0.5
        else:
            return 1/2/1e4*x*x+0.5

    def get_label(self):
        self.df_data['label'] = self.df_data['close'].diff()
        self.df_data['label'].fillna(0,inplace = True)
        self.df_data['label'] = self.df_data['label'].apply(self._transform_func_1)

        return self.df_data