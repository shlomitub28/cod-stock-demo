from alpha_vantage.timeseries import TimeSeries
import json
import argparse
import os
from csv import DictReader
from db import Db

def save_dataset(symbol, time_window):
    
    api_key = os.environ["API_KEY"]
    print(symbol, time_window)
    ts = TimeSeries(key=api_key, output_format='pandas')
    if time_window == 'intraday':
        data, meta_data = ts.get_intraday(
            symbol="{symbol}", interval='1min', outputsize='full')
    elif time_window == 'daily':
        data, meta_data = ts.get_daily(symbol, outputsize='full')
    elif time_window == 'daily_adj':
        data, meta_data = ts.get_daily_adjusted(symbol, outputsize='full')

    os.makedirs(f"./files/data/{symbol}", exist_ok=True)
    data.to_csv(f'./files/data/{symbol}/{symbol}_{time_window}.csv')
    

def upsert_data(symbol, time_window,records=100):
  print (f"Ingesting data for symbol {symbol}")
  total_records=0
  header = True
  with open(f'./files/data/{symbol}/{symbol}_{time_window}.csv', 'r') as read_obj:
    csv_dict_reader = DictReader(read_obj)
    model=Db()
    data = []
    i=1
    
    for row in csv_dict_reader:
      if header:
        header = False
        next
      data.append ([f"{symbol}",f"{row['date']}",\
                f"{row['1. open']}",f"{row['2. high']}",\
                f"{row['3. low']}",f"{row['4. close']}", \
                f"{row['5. volume']}"])
      total_records=total_records+1
      if i < records + 1 :   
        
        i=i+1
        
      else :
        
        model.upsert(data)
        data = []
        i=1
    
    if len(data) > 0 :
      model.upsert(data)
    print (f"Ingested {total_records} for symbol {symbol}")
          
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('symbol', type=str, help="the stock symbol you want to download")
    parser.add_argument('time_window', type=str, choices=[
                        'intraday', 'daily', 'daily_adj'], help="the time period you want to download the stock history for")

    namespace = parser.parse_args()
    save_dataset(**vars(namespace))
