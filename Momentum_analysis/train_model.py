from techinical_analysis import technical_analysis
import pandas as pd
from preprocessing import preprocessing
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import mean_squared_error
from parameters import train_model_date_split
import shap

class momentum_model(preprocessing):
    def __init__(self):
        super(momentum_model, self).__init__()

        self.df_data = self.get_label()
        self.ta = technical_analysis(self.df_data,'open','high','low','close','volume')
        self._get_technical_indicator()

    def _get_technical_indicator(self):
        self.df_ta = self.ta.pattern_recgonition()
        for func in dir(self.ta):
            if 'strategy' in func:
                self.df_ta[func] = getattr(self.ta,func)()

        #getattr(self.ta,)
        print('')

    def train_new_model(self):
        split = self.df_data[self.df_data['date'] < train_model_date_split].shape[0]
        df_train = self.df_ta.iloc[:split,:]
        label = self.df_data['label'].iloc[:split]
        self.X_train,X_test,self.y_train,y_test = train_test_split(df_train,label,test_size=0.2,random_state=42)
        lgb_train = lgb.Dataset(self.X_train,self.y_train,free_raw_data=False)
        lgb_eval = lgb.Dataset(X_test,y_test,reference=lgb_train,free_raw_data=False)
        params = {'boosting_type':'gbdt',
                  'objective':'regression',
                  'metric':{'l2','l1','min_gain_to_split'},
                  'num_leaves':30,
                  'learning_rate':0.05,
                  'feature_fraction':0.9,
                  'bagging_fraction':0.8,
                  'bagging_freq':5,
                  'verbose':0}
        gbm = lgb.LGBMRegressor()
        self.gbm = lgb.train(params,lgb_train,num_boost_round=1500,init_model=gbm,valid_sets=lgb_eval,early_stopping_rounds=300)
        y_pred = self.gbm.predict(X_test,num_iteration=self.gbm.best_iteration)
        print('the rmse of prediction is :',mean_squared_error(y_test,y_pred)**0.5)

    def predict_model(self):
        split = self.df_data[self.df_data['date'] < train_model_date_split].shape[0]
        df_test = self.df_ta.iloc[split:, :]
        label = self.df_data.iloc[split:]
        predict = self.gbm.predict(df_test,num_iteration=self.gbm.best_iteration)
        trial = pd.Series(predict,index = self.df_data[self.df_data['date'] > train_model_date_split]['date'])
        temp = []
        for true,pred in zip(label,predict):
            if (true >=0.5) & (pred >= 0.5):
                temp.append(1)
            elif (true <=0.5) &(pred <=0.5):
                temp.append(1)
            else:
                temp.append(-1)
        temp = pd.Series(temp)
        print('The precision is:',temp.value_counts()[1] /temp.size)
        return trial

    def feature_importance_plot(self,gbm):
        shap_values = shap.TreeExplainer(gbm).shap_values(self.X_train)
        shap.summary_plot(shap_values,self.X_train,plot_type='bar')



if __name__ == '__main__':
    model = momentum_model()
    model.train_new_model()
    trial = model.predict_model()
