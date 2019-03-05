import talib
import numpy as np
import historical_fx
import os
import datetime
# import plot_chart as plc
import matplotlib.pyplot as plt
# from matplotlib.finance import candlestick_ohlc as plot_candle
import time

class HILO:

    position = 0
    enter_p = -100
    profit = 0
    balance = 10000
    win_times = 0
    lose_times = 0
    win_combo = 1
    lose_combo = 1
    max_win_combo = 1
    max_lose_combo = 1
    last_unit_profit = 0

    def __init__(self):
        print("HILO initialized")
        self.btc_charts = historical_fx.charts()

    def get_price(self, num=1600, periods='1H'):
        (time_stamp, open_price, high_price, low_price, close_price) = self.btc_charts.get_price_array_till_finaltime(
            final_unixtime_stamp=time.time(), num=num, periods=periods, converter=True)
        return(time_stamp, open_price, high_price, low_price, close_price)


    def in_l(self,price):
        self.enter_p = price
        #self.position = self.balance / price
        if self.lose_combo > 2:
            self.position = 1 / self.lose_combo
        else:
            self.position = 1
        print('Long in %.0f'%(price))

    def in_s(self,price):
        self.enter_p = price
        #self.position = - self.balance / price
        if self.lose_combo > 2:
            self.position = 1 / self.lose_combo
        else:
            self.position = -1
        print('Short in %.0f'%(price))

    def qu_s(self,price):
        unit_profit = self.enter_p - price
        self.profit = -self.position * unit_profit
        self.balance = self.balance + self.profit
        self.enter_p = -100
        self.position = 0
        self.win_or_lose(unit_profit)
        print('Quit short in %.0f, profit: %.0f' % (price,unit_profit))
        print('Balance : %.0f\n' % hilo.balance)


    def qu_l(self,price):
        unit_profit = price - self.enter_p
        self.profit = self.position * unit_profit
        self.balance = self.balance + self.profit
        self.enter_p = -100
        self.position = 0
        self.win_or_lose(unit_profit)
        print('Quit long in %.0f, profit: %.0f' % (price, unit_profit))
        print('Balance : %.0f\n' % hilo.balance)

    def win_or_lose(self, unit_profit):
        if unit_profit > 0:
            self.win_times += 1
            if self.last_unit_profit > 0:
                self.win_combo += 1
                self.lose_combo = 1
                if self.win_combo >= self.max_win_combo:
                    self.max_win_combo = self.win_combo
        else:
            self.lose_times += 1
            if self.last_unit_profit < 0:
                self.lose_combo += 1
                self.win_combo = 1
                if self.lose_combo > self.max_lose_combo:
                    self.max_lose_combo = self.lose_combo
        self.last_unit_profit = unit_profit

    def get_loss(self):
        loss_factor = 0.015
        line = 0
        if self.position > 0:
            line = self.enter_p * (1-loss_factor)
        else:
            line = self.enter_p * (1+loss_factor)
        return line


    def multi_atr(self, high, low, close, timeperiod):
        multi_factor = [2.25, 2.25, 3]
        ema = np.array([talib.EMA(close.T[0], timeperiod)])
        atrs = np.array([talib.ATR(high.T[0], low.T[0], close.T[0], timeperiod)])
        atr_up_1 = ema + atrs * multi_factor[0] / 2
        atr_up_2 = ema + atrs * multi_factor[1] / 2
        atr_up_3 = ema + atrs * multi_factor[2] / 2

        atr_down_1 = ema - atrs * multi_factor[0] / 2
        atr_down_2 = ema - atrs * multi_factor[1] / 2
        atr_down_3 = ema - atrs * multi_factor[2] / 2
        return(atr_up_1[0],atr_up_2[0],atr_up_3[0],atr_down_1[0],atr_down_2[0],atr_down_3[0])


    def time2data(self, ts):
        print(ts[0].strftime('%Y-%m-%d %H:%M:%S'))

    def simulation(self):
        (time_stamp, open_price, high_price, low_price, close_price) = self.get_price()
        (atr_up_1, atr_up_2, atr_up_3, atr_down_1, atr_down_2, atr_down_3) = self.multi_atr(high_price, low_price, close_price, 18)

        datalen = len(open_price)
        for i in range(20, datalen):
            if self.position == 0:
                if high_price[i] > atr_up_1[i] and low_price[i] > atr_down_1[i]:
                    #TODO
                    #enter short
                    #self.in_s(close_price[i])
                    self.time2data(time_stamp[i])
                    self.in_s(atr_up_1[i])
                elif low_price[i] < atr_down_1[i] and high_price[i] < atr_up_1[i]:
                    #TODO
                    #self.in_l(close_price[i])
                    self.time2data(time_stamp[i])
                    self.in_l(atr_down_1[i])
                    #enter long
                    #enter short and loss cut
                else:
                    continue
            elif self.position > 0:
                loss_cut_line = self.get_loss()
                if low_price[i] < loss_cut_line:
                    #TODO
                    self.time2data(time_stamp[i])
                    print('Loss cut')
                    self.qu_l(loss_cut_line)
                    print('lose combo: %d'%(self.lose_combo))
                    #i = i+24
                    #q l
                    #loss cut
                    #continue
                elif high_price[i] > atr_up_1[i]:
                    self.time2data(time_stamp[i])
                    self.qu_l(atr_up_1[i])

                    self.time2data(time_stamp[i])
                    self.in_s(atr_up_1[i])
                    #self.in_s(close_price[i])
                    #cal_profit
                    #enter short
                else:
                    continue
            elif self.position < 0:
                loss_cut_line = self.get_loss()
                if high_price[i] > loss_cut_line:
                    #TODO
                    self.time2data(time_stamp[i])
                    print('Loss cut')
                    self.qu_s(loss_cut_line)
                    print('lose combo: %d' % (self.lose_combo))
                    #i = i + 24
                    #loss cut
                    #continue
                elif low_price[i] < atr_down_1[i]:
                    self.time2data(time_stamp[i])
                    self.qu_s(atr_down_1[i])

                    self.time2data(time_stamp[i])
                    self.in_l(atr_down_1[i])
                    #self.in_l(close_price[i])
                    #cal_profit
                    #enter long
                else:
                    continue



if __name__ == '__main__':
    # directly

    hilo = HILO()
    hilo.simulation()
    print(hilo.profit)
    print(hilo.max_win_combo)
    print(hilo.max_lose_combo)






    #(atr_up_1, atr_up_2, atr_up_3, atr_down_1, atr_down_2, atr_down_3 )= hilo.getATR()

