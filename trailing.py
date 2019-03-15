
import tradebf_basic
import predict
import time


class Trailing(tradebf_basic.Trade_basic):


    amount_pivot = 0.1
    amount_rsi = 0.1
    position_pivot = 0.0
    position_cdcrsi = 0.0


    enter_price = -100
    loss_cut_rate = 0.05
    take_profit = 0.1
    trailing_start = 0.02
    trailing_stop = 0.015

    def __init__(self):
        tradebf_basic.Trade_basic.__init__(self)
        print('trailing init')
        self.read_ini()
        self.set_vals()


    def set_vals(self):
        self.write_para2mem('amount_pivot', self.amount_pivot)
        self.write_para2mem('amount_rsi', self.amount_rsi)
        self.write_para2mem('position_pivot', self.position_pivot)
        self.write_para2mem('position_cdcrsi', self.position_cdcrsi)
        self.write_para2mem('enter_price', self.enter_price)

    def get_vals(self):
        self.amount_pivot = self.read_para2men('amount_pivot')
        self.amount_rsi = self.read_para2men('amount_rsi')
        self.position_pivot = self.read_para2men('position_pivot')
        self.position_cdcrsi = self.read_para2men('position_cdcrsi')
        self.enter_price = self.read_para2men('enter_price')

    def write_ini(self, config_file = './trade_basic.ini'):

        self.config['position'] = {'amount_pivot': '%.2f'%self.amount_pivot, 'amount_rsi': '%.2f'%self.amount_rsi,
                                   'position_pivot': '%.2f'%self.position_pivot, 'position_cdcrsi': '%.2f'%self.position_cdcrsi,
                                   'enter_price': '%.0f'%self.enter_price}
        with open(config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_ini(self, config_file = './trade_basic.ini'):
        self.config.read(config_file)
        self.amount_pivot = float(self.config.get('position', 'amount_pivot'))
        self.amount_rsi = float(self.config.get('position', 'amount_rsi'))
        self.position_pivot = float(self.config.get('position', 'position_pivot'))
        self.position_cdcrsi = float(self.config.get('position', 'position_cdcrsi'))
        self.enter_price = float(self.config.get('position', 'enter_price'))

    def iters(self):
        while 1:

            self.get_vals()
            if self.position_cdcrsi != 0.0:
                cur_time = time.gmtime()
                print('start a trailing order')
                retstr = self.trailing_loss_cut(cur_time)
                print(retstr)
            time.sleep(0.8)
            #except Exception:
            #    time.sleep(2)

    def print_position(self):
        predict.print_and_write('Total : %.2f, Pivot : %.2f, CDC : %.2f' % (
        self.position_pivot + self.position_cdcrsi, self.position_pivot, self.position_cdcrsi))

    def trailing_loss_cut(self, starttime):
        profit = 0
        max_profit = 0
        startt = self.bf_timejudge(starttime)
        trail_loss_cut = -self.loss_cut_rate * self.enter_price
        trail_take_profit = trail_loss_cut
        trail_max_profit = self.take_profit * self.enter_price
        temp_pre_profit = 0
        flag = True
        init_position = self.position_cdcrsi

        predict.print_and_write('Use a trial order')
        if self.enter_price == -100:
            predict.print_and_write('Enter pirce error')
            return('Enter pirce error')
        while self.position_cdcrsi != 0.0 and self.position_cdcrsi == init_position:
            cur_price = self.get_current_price(50)
            if self.position_cdcrsi > 0.0 and cur_price > 20000:
                profit = cur_price - self.enter_price
            elif self.position_cdcrsi < 0.0 and cur_price > 20000:
                profit = self.enter_price - cur_price
            else:
                print('error')
                continue

            # trailing
            if profit > max_profit:
                if not flag:
                    profit_gain = profit - max_profit
                    trail_take_profit = trail_take_profit + profit_gain
                max_profit = profit
                if max_profit >= self.trailing_start * self.enter_price and flag:
                    trail_take_profit = self.trailing_stop * self.enter_price
                    flag = False
            tdelta = self.bf_timejudge(starttime)
            dt = tdelta -startt
            print('T: %d, P: %5.0f, MP: %5.0f, L: %5.0f' % (dt, profit, max_profit, trail_take_profit), end='\r')

            #loss cut
            if profit < trail_take_profit or profit > trail_max_profit:
                if self.position_cdcrsi > 0.0:
                    trade_amount = self.position_cdcrsi
                    order = self.trade_market('sell', trade_amount)
                    self.position_cdcrsi = self.position_cdcrsi - trade_amount
                    self.enter_price = -100
                    self.print_position()
                    predict.print_and_write(order)
                    self.set_vals()
                    self.write_ini()
                    return ('Quit long')
                elif self.position_cdcrsi < 0.0:
                    trade_amount = self.position_cdcrsi
                    order = self.trade_market('buy', trade_amount)
                    self.position_cdcrsi = self.position_cdcrsi + trade_amount
                    self.enter_price = -100
                    self.print_position()
                    predict.print_and_write(order)
                    self.set_vals()
                    self.write_ini()
                    return ('Quit short')
            self.get_vals()
            time.sleep(0.8)
        return ('Quit cdc by other way')


if __name__ == '__main__':
    autoTrading = Trailing()
    autoTrading.iters()