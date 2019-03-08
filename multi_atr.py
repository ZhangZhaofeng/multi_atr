import talib
import numpy as np
import historical_fx
import os
import datetime
# import plot_chart as plc
import matplotlib.pyplot as plt
# from matplotlib.finance import candlestick_ohlc as plot_candle
import time
import pandas as pd


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
    leverage = 3
    balance_list = []

    def __init__(self):
        print("HILO initialized")
        self.btc_charts = historical_fx.charts()

    def get_price(self, num=3600, periods='2H'):
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
            self.position = -1 / self.lose_combo
        else:
            self.position = -1
        print('Short in %.0f'%(price))

    def loss_cut_position(self, loscutline, losscutpoint = 0.02):
        maxloss = abs(self.enter_p - loscutline)
        position_temp = (self.balance * self.leverage * losscutpoint) / maxloss
        if self.position < 0 :
            self.position = -position_temp

        elif self.position > 0:
            self.position = position_temp
        print('Position: %.4f' % (self.position))

    def qu_s(self,price):
        unit_profit = self.enter_p - price
        self.profit = -self.position * unit_profit
        self.balance = self.balance + self.profit
        self.enter_p = -100
        self.position = 0
        self.win_or_lose(unit_profit)
        print('Quit short in %.0f, profit: %.0f' % (price,unit_profit))
        print('Balance : %.0f\n' % hilo.balance)
        self.balance_list.append(hilo.balance)


    def qu_l(self,price):
        unit_profit = price - self.enter_p
        self.profit = self.position * unit_profit
        self.balance = self.balance + self.profit
        self.enter_p = -100
        self.position = 0
        self.win_or_lose(unit_profit)
        print('Quit long in %.0f, profit: %.0f' % (price, unit_profit))
        print('Balance : %.0f\n' % hilo.balance)
        self.balance_list.append(hilo.balance)

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

    def pivothilo(self, high, low, leftt, rightt):
        hi = high
        lo = low

        len_t = len(hi.T[0])
        pivothi = np.zeros(len_t)
        pivotlo = np.zeros(len_t)

        for i in range(0, len_t):
            if i < leftt or i+rightt+1 > len_t:
                continue
            flagh = True
            for li in range(1, leftt+1):
                if flagh and hi[i] <= hi[i-li]:
                    flagh = False
                    break
                elif not flagh:
                    break
                else:
                    continue
            for ri in range(1, rightt+1):
                if flagh and hi[i] <= hi[i+ri]:
                    flagh = False
                    break
                elif not flagh:
                    break
                else:
                    continue
            if flagh:
                pivothi[i] = hi[i]
            else:
                pivothi[i] = pivothi[i-1]

        for i in range(0, len_t):
            if i < leftt or i+rightt+1 > len_t:
                continue
            flagl = True
            for li in range(1, leftt+1):
                if flagl and lo[i] >= lo[i-li]:
                    flagl = False
                    break
                elif not flagl:
                    break
                else:
                    continue
            for ri in range(1, rightt+1):
                if flagl and lo[i] >= lo[i+ri]:
                    flagl = False
                    break
                elif not flagl:
                    break
                else:
                    continue
            if flagl:
                pivotlo[i] = lo[i]
            else:
                pivotlo[i] = pivotlo[i-1]


        for fi in range(0, rightt):
            pivothi[-fi - 1] = pivothi[-rightt - 1]
            pivotlo[-fi - 1] = pivotlo[-rightt - 1]


        return(pivothi,pivotlo)


    def dc(self, high, low, timeperiod):
        max_price = np.array([talib.MAX(high.T[0], timeperiod)])
        min_price = np.array([talib.MIN(low.T[0], timeperiod)])
        return(max_price, min_price)


    def dc_filter(self, close, high, low, timeperiod):
        (max_p , min_p) = self.dc(high, low, timeperiod)
        filtered = []
        datalen = len(max_p[0])
        for i in range(20, datalen):
            if close[i] > max_p[0][i-1] :
                filtered.append(1)
            elif close[i] < min_p[0][i-1] :
                filtered.append(2)
            else:
                filtered.append(0)
        return filtered

    def time2data(self, ts):
        print(ts[0].strftime('%Y-%m-%d %H:%M:%S'))

    def simulation_pivot(self):
        (time_stamp, open_price, high_price, low_price, close_price) = self.get_price()
        (pivothi, pivotlo) = self.pivothilo(high_price, low_price, 4, 2)
        #TODO
        datalen = len(open_price)
        for i in range(40, datalen):
            if self.position == 0:
                if high_price[i] > pivothi[i]:
                    self.time2data(time_stamp[i])
                    self.in_l(pivothi[i])
                    #self.loss_cut_position(pivotlo[i])
                elif low_price[i] < pivotlo[i]:
                    self.time2data(time_stamp[i])
                    self.in_s(pivotlo[i])
                    #self.loss_cut_position(pivothi[i])
                else:
                    continue
            elif self.position > 0:
                if low_price[i] < pivotlo[i]:
                    self.time2data(time_stamp[i])
                    self.qu_l(pivotlo[i])


                    self.time2data(time_stamp[i])
                    self.in_s(pivotlo[i])
                    #self.loss_cut_position(pivothi[i])
                else:
                    continue
            elif self.position < 0:
                if high_price[i] > pivothi[i]:
                    self.time2data(time_stamp[i])
                    self.qu_s(pivothi[i])


                    self.time2data(time_stamp[i])
                    self.in_l(pivothi[i])
                    #self.loss_cut_position(pivotlo[i])
                else:
                    continue


    def simulation(self):
        (time_stamp, open_price, high_price, low_price, close_price) = self.get_price()
        (atr_up_1, atr_up_2, atr_up_3, atr_down_1, atr_down_2, atr_down_3) = self.multi_atr(high_price, low_price, close_price, 18)
        #filtered = self.dc_filter(close_price, high_price, low_price, 40)
        (dc_max , dc_min) = self.dc(high_price, low_price, 40)
        datalen = len(open_price)
        enter_flag = 0
        for i in range(40, datalen):
            if enter_flag > 0:
                enter_flag -= 1
                print('Last %d times'%enter_flag)
            if self.position == 0:
                if high_price[i] > atr_up_1[i] and low_price[i] > atr_down_1[i] and dc_min[0][i-1] < close_price[i] and enter_flag == 0 :
                    #TODO
                    #enter short
                    #self.in_s(close_price[i])
                    self.time2data(time_stamp[i])
                    self.in_s(atr_up_1[i])
                elif low_price[i] < atr_down_1[i] and high_price[i] < atr_up_1[i] and dc_max[0][i-1] > close_price[i] and enter_flag == 0 :
                    #TODO
                    #self.in_l(close_price[i])
                    self.time2data(time_stamp[i])
                    self.in_l(atr_down_1[i])
                    #enter long
                    #enter short and loss cut
                elif dc_min[0][i-1] > close_price[i] or dc_max[0][i-1] < close_price[i]:
                    print('Not enter for 5 times')
                    enter_flag = 5
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
                elif high_price[i] > atr_up_1[i] and close_price[i] < dc_max[0][i-1] and enter_flag == 0 :
                    self.time2data(time_stamp[i])
                    self.qu_l(atr_up_1[i])

                    self.time2data(time_stamp[i])
                    self.in_s(atr_up_1[i])
                    #self.in_s(close_price[i])
                    #cal_profit
                    #enter short
                elif close_price[i] > dc_max[0][i-1]:
                    print('Not enter for 5 times')
                    self.time2data(time_stamp[i])
                    self.qu_l(close_price[i])
                    enter_flag = 5
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
                elif low_price[i] < atr_down_1[i] and close_price[i] > dc_min[0][i-1] and enter_flag == 0 :
                    self.time2data(time_stamp[i])
                    self.qu_s(atr_down_1[i])

                    self.time2data(time_stamp[i])
                    self.in_l(atr_down_1[i])
                    #self.in_l(close_price[i])
                    #cal_profit
                    #enter long
                elif close_price[i] < dc_min[0][i-1]:
                    self.time2data(time_stamp[i])
                    self.qu_s(close_price[i])
                    print('Not enter for 5 times')
                    enter_flag = 5
                else:
                    continue

    def balance_sta(self):
        maxi = self.balance_list[0]
        max_lose_rate = 0
        balance_len = len(self.balance_list)
        for i in self.balance_list:
            if i >= maxi:
                maxi = i
            elif i < maxi:
                lose_rate = (maxi -i) / maxi
                if lose_rate > max_lose_rate:
                    max_lose_rate = lose_rate
        print(max_lose_rate)



if __name__ == '__main__':
    # directly

    hilo = HILO()
    (time_stamp, open_price, high_price, low_price, close_price) = hilo.get_price()


    hilo.simulation_pivot()
    hilo.balance_sta()
    #print(hilo.profit)
    #print(hilo.max_win_combo)
    #print(hilo.max_lose_combo)






    #(atr_up_1, atr_up_2, atr_up_3, atr_down_1, atr_down_2, atr_down_3 )= hilo.getATR()

