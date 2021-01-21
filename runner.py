%load_ext autoreload
%autoreload 2
from tech_ind_model import run_model
from get_stock_data import get_dataset , upsert_data
from predict import Predict
import time
import os.path
from os import path

symbols=['NLOK','AMD','QRVO','NVDA','AAPL','AMZN','GOOGL','FB','ORCL','CSCO','IBM','UBER','LYFT','COST',
         'MCD','BA','AAL','MSFT','GM','KO','QCOM','BABA','UAA','SCON','HPQ','ZNGA','GM','QCOM','JBLU','XRX']
not_to_use = []
bought=['MCD','NKE','ZNGA','BABA','AMZN','QRVO','COST','MSFT']
test = ['ADBE']
t = 1
for symbol in test:
    data = get_dataset(symbol,'daily')
    upsert_data(symbol,data)
    run_model(symbol,True)
    p = Predict(symbol)
    p.prediction(120)
    p.calculate_earnings()
    if t==5:
        t=0
        time.sleep(61)
    t+=1
