from tech_ind_model import run_model
from save_data_to_csv import save_dataset
from predict import Predict
import time
import os.path
from os import path

symbols=['NLOK','AMD','QRVO','NVDA','AAPL','AMZN','GOOGL','FB','ORCL','CSCO','IBM','UBER','LYFT','COST',
         'MCD','BA','AAL','MSFT','GM','KO','QCOM','BABA','UAA','SCON','HPQ','ZNGA','GM','QCOM','JBLU','XRX']
not_to_use = []
bought=['MCD','NKE','ZNGA','BABA','AMZN','QRVO','COST','MSFT']
t = 1
for symbol in symbols:
    save_dataset(symbol,'daily')
    run_model(symbol)
    p = Predict(symbol)
    p.prediction(120)
    p.calculate_earnings()
    if t==5:
        t=0
        time.sleep(61)
    t+=1

"""

p = Predict('MSFT')
p.prediction(120)
p.calculate_earnings()
"""