import talib
import numpy as np
import historical_fx
import os

# import plot_chart as plc
import matplotlib.pyplot as plt
# from matplotlib.finance import candlestick_ohlc as plot_candle
import time

class HILO:



    def __init__(self):
        print("HILO initialized")
        self.btc_charts = historical_fx.charts()

    def getATR(self, num=400, periods='1H'):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)
        self.multi_atr(high_price, low_price, close_price, 18)



    def multi_atr(self, high, low, close, timeperiod):
        multi_factor = [1.25, 2.25, 3]
        ema = np.array([talib.EMA(close.T[0], timeperiod)])
        atrs = np.array([talib.ATR(high.T[0], low.T[0], close.T[0], timeperiod)])
        atr_up_1 = ema + atrs * multi_factor[0] / 2
        atr_up_2 = ema + atrs * multi_factor[1] / 2
        atr_up_3 = ema + atrs * multi_factor[2] / 2

        atr_down_1 = ema - atrs * multi_factor[0] / 2
        atr_down_2 = ema - atrs * multi_factor[1] / 2
        atr_down_3 = ema - atrs * multi_factor[2] / 2
        return(atr_up_1,atr_up_2,atr_up_3,atr_down_1,atr_down_2,atr_down_3)


if __name__ == '__main__':
    # directly

    hilo = HILO()
    hilo.getATR()

    #(atr_up_1, atr_up_2, atr_up_3, atr_down_1, atr_down_2, atr_down_3 )= hilo.getATR()

