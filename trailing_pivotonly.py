
import tradebf_basic
import predict
import time,math


class Trailing(tradebf_basic.Trade_basic):


    amount_pivot = 0.0
    position_pivot = 0.0


    enter_price = -100
    loss_cut_rate = 0.022
    loss_cut_rate_force = 0.035
    take_profit = 0.2
    trailing_start = 0.1
    trailing_stop = 0.08

    add_step = 0.6 # add position step: 0.6 atr
    max_step = 3
    cur_step = 0




    def __init__(self):
        tradebf_basic.Trade_basic.__init__(self)
        print('trailing init')
        self.read_ini()
        self.set_vals()


    def write_ini(self, config_file = './trade_basic_pivot.ini'):

        self.config['position'] = {'amount_pivot': '%.2f'%self.amount_pivot,
                                   'position_pivot': '%.2f'%self.position_pivot,
                                   'enter_price': '%.0f'%self.enter_price}
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_ini(self, config_file = './trade_basic_pivot.ini'):
        self.config.read(config_file)
        self.amount_pivot = float(self.config.get('position', 'amount_pivot'))
        self.position_pivot = float(self.config.get('position', 'position_pivot'))
        self.enter_price = float(self.config.get('position', 'enter_price'))


    def set_vals(self):
        self.write_para2mem('amount_pivot', self.amount_pivot)
        self.write_para2mem('position_pivot', self.position_pivot)
        self.write_para2mem('enter_price', self.enter_price)

    def get_vals(self):
        self.amount_pivot = float(self.read_para2men('amount_pivot'))
        self.position_pivot = float(self.read_para2men('position_pivot'))
        self.enter_price = float(self.read_para2men('enter_price'))


    def iters(self):
        while 1:

            self.get_vals()
            if self.position_pivot != 0.0:
                cur_time = time.gmtime()
                print('start a trailing order')
                atr = self.get_ATR()
                retstr = self.trailing_loss_cut(cur_time, atr)
                print(retstr)
            time.sleep(0.8)
            #except Exception:
            #    time.sleep(2)

    def print_position(self):
        predict.print_and_write('Pivot : %.2f'%(float(self.position_pivot)))



    def trailing_loss_cut(self, starttime, atr):
        #profit = 0
        max_profit = 0
        startt = self.bf_timejudge(starttime) # start time ( num)
        #tdelta = self.bf_timejudge(starttime)
        #trail_loss_cut = -self.loss_cut_rate * self.enter_price # init loss cut price usually 2.2 atr
        #trail_loss_cut =

        trail_take_profit = -2.2 * atr
        inital_lc_line = trail_take_profit
        trail_take_profit_force = -4.4 * atr
        inital_lc_line_force = trail_take_profit_force
        temp2 = -self.loss_cut_rate_force * self.enter_price
        if temp2 < trail_take_profit_force:
            trail_take_profit_force = temp2

        trail_max_profit = self.take_profit * self.enter_price
        #temp_pre_profit = 0
        flag = True
        init_position = self.position_pivot
        dt = 0
        update_flag = True # update trailing acc
        trailing_factor = 0.2
        trailing_acc = 0.1  # add acc ever hour
        trailing_max = 1  # acc max to this
        loss_cut_count = 0
        loss_cut_count_start = False

        predict.print_and_write('Use a trial order')
        if self.enter_price == -100:
            predict.print_and_write('Enter pirce error')
            return('Enter pirce error')
        while self.position_pivot != 0.0 and self.position_pivot == init_position:
            cur_price = self.get_current_price(50)
            if self.position_pivot > 0.0 and cur_price > 20000:
                profit = cur_price - self.enter_price
            elif self.position_pivot < 0.0 and cur_price > 20000:
                profit = self.enter_price - cur_price
            else:
                print('error')
                continue

            # trailing
            if profit > max_profit:
                # if max profit reached: update trailing factor ever hour
                if update_flag:
                    trailing_factor += trailing_acc
                    if trailing_factor > trailing_max:
                        trailing_factor = trailing_max
                    update_flag = False
                    predict.print_and_write('Trailing factor updated %.2f' % (trailing_factor))

                if loss_cut_count_start: # if start to count loss cut, quit
                    loss_cut_count_start = False
                    loss_cut_count = 0
                    predict.print_and_write('Loss cut statues released')

                profit_gain = profit * trailing_factor # trailing values
                trail_take_profit = math.floor(inital_lc_line + profit_gain)
                trail_take_profit_force = math.floor(inital_lc_line_force + profit_gain)
                max_profit = profit

                #if max_profit >= self.trailing_start * self.enter_price and flag:
                #    new_trail_take_profit = self.trailing_stop * self.enter_price
                #    if new_trail_take_profit > trail_take_profit:
                #        print('init loss cut line updated to trailing stop point')
                #        inital_lc_line = new_trail_take_profit - profit_gain
                #        trail_take_profit = inital_lc_line + profit_gain
                #    flag = False
            tdelta = self.bf_timejudge(starttime)
            ds = tdelta - startt
            if loss_cut_count_start:
                print('Wait to quit, LC: %3d,  P: %6.0f, MP: %6.0f, L: %6.0f' % (loss_cut_count, profit, max_profit, trail_take_profit),
                      end='\r')
            else:
                print('H: %2d, S: %4d, P: %6.0f, MP: %6.0f, L: %6.0f' % (dt, ds, profit, max_profit, trail_take_profit),
                      end='\r')
            if ds > 1800:
            # if hour changed reset time
                startt = tdelta
                ds = 0
                dt += 1
                if update_flag == True and dt%4 == 0: # update trailing factor each 2 hour
                    trailing_factor += trailing_acc
                    if trailing_factor > trailing_max:
                        trailing_factor = trailing_max
                    predict.print_and_write('Trailing factor updated %.2f' % (trailing_factor)) # if max profit not updated in this hour forcely update the trailing factor
                    profit_gain = max_profit * trailing_factor
                    trail_take_profit = math.floor(inital_lc_line + profit_gain)
                    trail_take_profit_force = math.floor(inital_lc_line_force + profit_gain)

                else:
                    update_flag = True

            #loss cut
            if profit < trail_take_profit or profit > trail_max_profit or loss_cut_count_start:
                if loss_cut_count <= 300: # protect the price not break too soon
                    loss_cut_count_start = True

                if self.position_pivot > 0.0 and (loss_cut_count > 300 or profit < trail_take_profit_force):
                    if profit < trail_take_profit_force:
                        predict.print_and_write('Last line toched quit immediately')
                    trade_amount = abs(self.position_pivot)
                    order = self.trade_market('sell', trade_amount, cur_price)
                    self.position_pivot = self.position_pivot - trade_amount
                    self.enter_price = -100
                    self.print_position()
                    predict.print_and_write(order)
                    self.set_vals()
                    self.write_ini()
                    return ('Quit long')
                elif self.position_pivot < 0.0 and (loss_cut_count > 300 or profit < trail_take_profit_force):
                    if profit < trail_take_profit_force:
                        predict.print_and_write('Last line touched quit immediately')
                    trade_amount = abs(self.position_pivot)
                    order = self.trade_market('buy', trade_amount, cur_price)
                    self.position_pivot = self.position_pivot + trade_amount
                    self.enter_price = -100
                    self.print_position()
                    predict.print_and_write(order)
                    self.set_vals()
                    self.write_ini()
                    return ('Quit short')
            self.get_vals()
            if loss_cut_count_start:
                loss_cut_count += 1
            time.sleep(0.8)

        return ('Quit pivot by other way')


if __name__ == '__main__':
    autoTrading = Trailing()
    autoTrading.iters()