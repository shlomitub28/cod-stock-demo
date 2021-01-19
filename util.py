import pandas as pd
from sklearn import preprocessing
import numpy as np
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
history_points = 50
from db import Db
import sys


def get_raw_data(symbol,print_sample=True):
    """
    data = pd.read_csv(f'./files/data/{symbol}/{symbol}_daily.csv')
    data = data.drop('date', axis=1)
    data = data.drop(0, axis=0)
    print(data.head(5))
    print(data.count())
    """
    model = Db()
    records = model.get_data(symbol)
    
    data = pd.DataFrame(data = records, 
                         columns = ['open_val','high_val','low_val','close_val','volume'])
    data = data.drop(0, axis=0)
    if print_sample:
      print(data.head(5))
      print(data.count())
    return data.to_numpy()


def csv_to_dataset(symbol):
    data = get_raw_data(symbol)
    data_normaliser = preprocessing.MinMaxScaler()
    data_normalised = data_normaliser.fit_transform(data)
    ohlcv_histories_normalised = get_ohlcv_histories_normalised(data_normalised)

    next_day_open_values_normalised = np.array(
        [data_normalised[:, 0][i + history_points].copy() for i in range(len(data_normalised) - history_points)])
    next_day_open_values_normalised = np.expand_dims(next_day_open_values_normalised, -1)

    next_day_open_values = get_next_day_open_values(data)

    y_normaliser = get_y_normaliser(next_day_open_values)

    technical_indicators_normalised = get_technical_indicators(ohlcv_histories_normalised)

    assert ohlcv_histories_normalised.shape[0] == next_day_open_values_normalised.shape[0] == \
           technical_indicators_normalised.shape[0]
    return ohlcv_histories_normalised, technical_indicators_normalised, next_day_open_values_normalised, \
           next_day_open_values, y_normaliser
def get_y_normaliser(data):
    y_normaliser = preprocessing.MinMaxScaler()
    y_normaliser.fit(data)
    return y_normaliser
def get_next_day_open_values(data):
    next_day_open_values = np.array([data[:, 0][i + history_points].copy() for i in range(len(data) - history_points)])
    next_day_open_values = np.expand_dims(next_day_open_values, -1)
    return next_day_open_values

def get_ohlcv_histories_normalised(data_normalised, last=0):
    # using the last {history_points} open close high low volume data points, predict the next open value
    if (last == 0):
        rng = range(len(data_normalised) - history_points)
    else:
        rng = range(len(data_normalised) - history_points + 1 - last, len(data_normalised) - history_points + 2)
    return np.array(
        [data_normalised[i:i + history_points].copy() for i in rng])


def get_next_day_open_values_normalised(data_normalised, last=0):
    # using the last {history_points} open close high low volume data points, predict the next open value
    if (last == 0):
        rng = range(len(data_normalised) - history_points)
    else:
        rng = range(len(data_normalised) - history_points + 1 - last, len(data_normalised) - history_points + 2)
    return np.array(
        [data_normalised[i:i + history_points].copy() for i in rng])


def get_technical_indicators(ohlcv_histories_normalised):
    technical_indicators = []
    for his in ohlcv_histories_normalised:
        # note since we are using his[3] we are taking the SMA of the closing price
        sma = np.mean(his[:, 3])
        macd = calc_ema(his, 12) - calc_ema(his, 26)
        technical_indicators.append(np.array([sma]))
        # technical_indicators.append(np.array([sma,macd,]))

    technical_indicators = np.array(technical_indicators)

    tech_ind_scaler = preprocessing.MinMaxScaler()
    return tech_ind_scaler.fit_transform(technical_indicators)


def calc_ema(values, time_period):
    # https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp
    sma = np.mean(values[:, 3])
    ema_values = [sma]
    k = 2 / (1 + time_period)
    for i in range(len(values) - time_period, len(values)):
        close = values[i][3]
        ema_values.append(close * k + ema_values[-1] * (1 - k))
    return ema_values[-1]


def multiple_csv_to_dataset(test_set_name):
    import os
    ohlcv_histories = 0
    technical_indicators = 0
    next_day_open_values = 0
    for csv_file_path in list(filter(lambda x: x.endswith('daily.csv'), os.listdir('./'))):
        if not csv_file_path == test_set_name:
            print(csv_file_path)
            if type(ohlcv_histories) == int:
                ohlcv_histories, technical_indicators, next_day_open_values, _, _ = csv_to_dataset(csv_file_path)
            else:
                a, b, c, _, _ = csv_to_dataset(csv_file_path)
                ohlcv_histories = np.concatenate((ohlcv_histories, a), 0)
                technical_indicators = np.concatenate((technical_indicators, b), 0)
                next_day_open_values = np.concatenate((next_day_open_values, c), 0)

    ohlcv_train = ohlcv_histories
    tech_ind_train = technical_indicators
    y_train = next_day_open_values

    ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser = csv_to_dataset(test_set_name)

    return ohlcv_train, tech_ind_train, y_train, ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser
