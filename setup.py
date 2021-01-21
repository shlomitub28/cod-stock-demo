%load_ext autoreload
%autoreload 2
import logging
from db import Db
from get_stock_data import upsert_data, get_dataset
#logging.basicConfig( level=logging.DEBUG)
symbol='AAPL'
model=Db()
#model.drop_stocks_table()
#model.create_stock_table()
model.delete_data(symbol)
data = get_dataset(symbol,'daily')
upsert_data(symbol,data)
model.get_data_stat(symbol)