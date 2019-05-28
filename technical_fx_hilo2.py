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


    def get_price(self, num=100, periods="1H"):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)
        return(time_stamp, open_price, high_price, low_price, close_price)

    def publish_current_hilo_price(self, num=100, periods="1H"):
        #(time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
        #    final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)

        (time_stamp, open_price, high_price, low_price, close_price) = self.get_price()
        low_price_ma = self.get_short_price(low_price)
        high_price_ma = self.get_long_price(high_price)
        (buyprice, sellprice)=(high_price_ma[-2][0],low_price_ma[-2][0])
        a=(int(buyprice), int(sellprice))
        return (int(buyprice), int(sellprice), int(close_price[-1]), int(high_price[-1]), int(low_price[-1]))

    def getATR(self, num=100, periods = '1H'):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)
        ATRs = self.ATR(high_price, low_price, close_price)
        return ATRs[-1]

    def pivothilo(self, leftt, rightt):

        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=100, periods='2H', converter=True)


        hi = high_price[1:]
        lo = low_price[1:]

        len_t = len(hi.T[0])
        pivothi = np.zeros(len_t)
        pivotlo = np.zeros(len_t)

        for i in range(0, len_t):
            if i < leftt or i + rightt + 1 > len_t:
                continue
            flagh = True
            for li in range(1, leftt + 1):
                if flagh and hi[i] <= hi[i - li]:
                    flagh = False
                    break
                elif not flagh:
                    break
                else:
                    continue
            for ri in range(1, rightt + 1):
                if flagh and hi[i] <= hi[i + ri]:
                    flagh = False
                    break
                elif not flagh:
                    break
                else:
                    continue
            if flagh:
                pivothi[i + rightt] = hi[i]
            else:
                pivothi[i + rightt] = pivothi[i + rightt - 1]

        for i in range(0, len_t):
            if i < leftt or i + rightt + 1 > len_t:
                continue
            flagl = True
            for li in range(1, leftt + 1):
                if flagl and lo[i] >= lo[i - li]:
                    flagl = False
                    break
                elif not flagl:
                    break
                else:
                    continue
            for ri in range(1, rightt + 1):
                if flagl and lo[i] >= lo[i + ri]:
                    flagl = False
                    break
                elif not flagl:
                    break
                else:
                    continue
            if flagl:
                pivotlo[i + rightt] = lo[i]
            else:
                pivotlo[i + rightt] = pivotlo[i + rightt - 1]

        # for fi in range(0, rightt):
        #    pivothi[-fi - 1] = pivothi[-rightt - 1]
        #    pivotlo[-fi - 1] = pivotlo[-rightt - 1]


        return (pivothi, pivotlo)


if __name__ == '__main__':
    hilo = HILO()
    ATRs = hilo.getATR()
    print(ATRs)