#!/usr/bin/python3
# coding=utf-8


import talib
import numpy as np
import historical_fx
import time


class HILO:
    def __init__(self):
        print("HILO initialized")
        self.btc_charts = historical_fx.charts()

    def MA(self, ndarray, timeperiod=5):
        x = np.array([talib.MA(ndarray.T[0], timeperiod)])
        # print(x)
        return x.T

    def ATR(self, high, low, close, timeperiod=4):
        x = np.array([talib.ATR(high.T[0], low.T[0], close.T[0], timeperiod)])
        return x.T

    def get_HIGH_MA(self, HIGH):  # price=1*N (N>61)
        ma_high=self.MA(HIGH,15)
        return ma_high

    def get_LOW_MA(self, LOW):  # price=1*N (N>61)
        ma_low=self.MA(LOW,15)
        return ma_low

    def get_long_price(self, HIGH):
        ma_high=self.get_HIGH_MA(HIGH)
        return ma_high

    def get_short_price(self, LOW):
        ma_low = self.get_LOW_MA(LOW)
        return ma_low

    def publish_current_hilo_price(self, num=100, periods="1H"):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)

        low_price_ma = self.get_short_price(low_price)
        high_price_ma = self.get_long_price(high_price)
        (buyprice, sellprice)=(high_price_ma[-2][0],low_price_ma[-2][0])
        a=(int(buyprice), int(sellprice))
        return (int(buyprice), int(sellprice), int(close_price[-1]), int(high_price[-1]), int(low_price[-1]))

    def getATR(self, num=400, periods = '1H'):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)
        ATRs = self.ATR(high_price, low_price, close_price)
        return ATRs[-1]

if __name__ == '__main__':
    hilo = HILO()
    ATRs = hilo.getATR()
    print(ATRs)