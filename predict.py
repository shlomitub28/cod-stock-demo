import numpy as np
from keras.models import load_model
from util import create_dataset, history_points, get_raw_data, get_ohlcv_histories_normalised, get_technical_indicators \
    , get_next_day_open_values
from sklearn import preprocessing


class Predict():
    def __init__(self, symbol):
        self.model = load_model(f'./files/models/{symbol}/{symbol}_technical_model.h5')
        self.thresh = 0.005
        self.symbol = symbol
        self.current_price = []
        self.predicted_price = []
        self.recommandations = []
        self.current_recommandation = ""
        self.predicted_open_price_tomorrow = 0

    def prediction(self, last=0):
        start = 0
        end = -1
        ohlcv_test_last, tech_ind_test_last, data_normaliser, y_normaliser = self.predict_last_values(self.symbol, last)
        for ohlcv, ind in zip(ohlcv_test_last[start: end], tech_ind_test_last[start: end]):
            normalised_price_today = ohlcv[-1][0]
            normalised_price_today = np.array([[normalised_price_today]])
            price_today = y_normaliser.inverse_transform(normalised_price_today)
            # print(f"price_today last:{price_today}")
            npohlcv = np.array([ohlcv])
            npind = np.array([ind])
            pred = self.model.predict([npohlcv, npind])
            predicted_price_tomorrow = np.squeeze(y_normaliser.inverse_transform(pred)).item()
            # print(f"predicted_price_tomorrow:{predicted_price_tomorrow}")
            self.current_price.append(price_today[0][0])
            self.predicted_price.append(predicted_price_tomorrow)

    def collect_earnings(self):
        x = 0
        transactions = "buy"
        signal = ""

        for price in self.current_price:
            if x == 0:
                starting_price = price
                real_prev_price = price
                last_pred_price = self.predicted_price[0]
                x += 1
                continue
            delta = 1 - self.predicted_price[x]/last_pred_price
            if delta < 0:
                signal = "positive"
                if transactions == "sell" or transactions == "dont buy":
                    transactions = "buy"
                elif transactions == "buy" or transactions == "keep":
                    transactions = "keep"
            elif delta > 0:
                signal = "negative"
                if transactions == "sell" or transactions == "dont buy":
                    transactions = "dont buy"
                else:
                    transactions = "sell"
            else:
                signal = "same"
            if delta < -  self.thresh:
                signal = "high"
            elif delta > self.thresh:
                signal = "low"


                # if transactions == "buy" or transactions == "" or transactions == "keep":
                #   self.recommandations.append({"sell": price})
                #    transactions = "sell"
            self.recommandations.append(
                {"recommendation": transactions, "last predicted":last_pred_price,"price": price,
                 "predicted": self.predicted_price[x], "signal": signal})
            last_pred_price = self.predicted_price[x]


            x += 1
        self.predicted_open_price_tomorrow = last_pred_price
        

    def calculate_earnings(self):
        self.collect_earnings()
        revenue = 0
        prev_price = -1
        first_price = 0
        for trans in self.recommandations:
            
            if prev_price == -1:
                if trans['signal'] == "negative" or trans['signal'] == "low":
                    continue
                else:
                    prev_price = trans['price']
                    first_price = trans['price']
                    first_predicted = trans['predicted']
                    prev_predicted = trans['predicted']
                    

                    continue
            if trans['recommendation'] == "buy":
                #if trans['predicted'] > prev_predicted:
                prev_price = trans['price']
                prev_predicted = trans['last predicted']
            elif trans['recommendation'] == "sell":
                # print(f"sold in {value}")
                #if prev_predicted < trans['predicted']:

                revenue += trans['price'] - prev_price
                ###print(f"revenue:{revenue}")
                # print(f"revenue  here  {value - prev_price}")
        percent = (revenue / first_price) * 100
        print(trans)
        print(f"symbol-{self.symbol}:revenue {revenue}:revenue % {percent} %:first price {first_price}"
              f":last price {trans['price']}:predicted price {self.predicted_open_price_tomorrow}:"
              f" recommandation {trans['recommendation']}: signal {trans['signal']}")
        # return revenue, percent, first_price,value,

    def predict_last_values(self, symbol, last=0):
        data = get_raw_data(symbol,False)
        data_normaliser = preprocessing.MinMaxScaler()
        data_normalised = data_normaliser.fit_transform(data)
        next_day_open_values = get_next_day_open_values(data)
        y_normaliser = preprocessing.MinMaxScaler()
        y_normaliser.fit(next_day_open_values)
        ohlcv_histories_normalised = get_ohlcv_histories_normalised(data_normalised, last)
        technical_indicators_normalised = get_technical_indicators(ohlcv_histories_normalised)
        return ohlcv_histories_normalised, technical_indicators_normalised, data_normaliser, y_normaliser
