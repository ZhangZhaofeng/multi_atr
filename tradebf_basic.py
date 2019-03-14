from tradingapis.bitflyer_api import pybitflyer
import keysecret as ks
import time
import predict
#import configIO
#import sys
import math
import notify
import data2csv
import memcache




class Trade_basic():

    auto_decide = True
    total_margin = 50000
    least_collateral = 15000
    useable_margin = 35000
    level = 3
    max_loss = 0.03


    def __init__(self):
        print("Initializing API")
        self.bitflyer_api = pybitflyer.API(api_key=str(ks.bitflyer_api), api_secret=str(ks.bitflyer_secret))
        self.shared = memcache.Client(['127.0.0.1:11211'], debug=0)

    def write_para2mem(self, name, val):
        self.shared.set(name, val)

    def read_para2men(self, name):
        return(self.shared.get(name))

    def decide_trade_amount(self, curp ,losscut):
        safe_trade = 0.1
        if self.auto_decide:
            while curp == 0.0:
                predict.print_and_write('curp == 0 try again')
                curp = self.get_current_price(30)
            max_trade = round(self.useable_margin * self.level / curp, 2)
            safe_trade = round(self.useable_margin * self.max_loss / losscut, 2)
            predict.print_and_write('Amount control, Max trade: %.2f, safe trade: %.2f' % (max_trade, safe_trade))
            if safe_trade > max_trade:
                predict.print_and_write('Use smaller')
                safe_trade = max_trade
            self.init_trade_amount_buy = safe_trade
            self.init_trade_amount_sell = safe_trade

    def trade_market(self, type, amountin, wprice = 10000):
        self.maintance_time()

        product = 'FX_BTC_JPY'
        print('trade bitflyer')
        expire_time = 575
        try_t = 0
        amount = '%.2f'%(float(amountin))
        while try_t < 20:
            if type == 'BUY' or type == 'buy':
                #order = self.bitflyer_api.sendchildorder(product_code=product, child_order_type='MARKET',
                #    side='BUY', size= str(amount))
                order = 'child_order_acceptance_id, buy'
                data2csv.data2csv(
                    [time.strftime('%b:%d:%H:%M'), 'order', 'BUY_MARKET', 'amount', '%f' % float(amount)])
                predict.print_and_write('Buy market ' +str(amount))
            elif type == "SELL" or type == "sell":
                #order = self.bitflyer_api.sendchildorder(product_code=product, child_order_type='MARKET',
                #                                         side='SELL', size=str(amount))
                order = 'child_order_acceptance_id, sell'
                data2csv.data2csv(
                    [time.strftime('%b:%d:%H:%M'), 'order', 'SELL_MARKET', 'amount', '%f' % float(amount)])
                predict.print_and_write('Sell market ' +str(amount))
            else:
                print("error!")
            if 'child_order_acceptance_id' in order:
                time.sleep(2)
                execute_price = self.get_execute_order()
                if execute_price != 0:
                    if type == "SELL" or type == "sell":
                        slides = float(wprice) - float(execute_price)
                        predict.print_and_write('SELL : Wish price: %f, deal price: %f, slide : %f'%(wprice, execute_price, slides))
                        notify.notify_it('SELL : Price: %f, amount : %f'%(wprice, float(amount)))
                    elif type == "BUY" or type == "buy":
                        slides = float(execute_price) - float(wprice)
                        predict.print_and_write('BUY : Wish price: %f, deal price: %f, slide : %f'%(wprice, execute_price, slides))
                        notify.notify_it('BUY : Price: %f, amount : %f' % (wprice, float(amount)))
                return order
            else:
                try_t += 1
                print(order)
                print('Failed, try again')
                time.sleep(20)


    # deal with maintance time
    def maintance_time(self):
        while 1:
            cur_oclock = int(time.strftime('%H:')[0:-1])
            cur_min = int(time.strftime('%M:')[0:-1])
            if (cur_oclock == 4 and cur_min >= 0 and cur_min <= 12) or (cur_oclock == 3 and cur_min >= 58):
                predict.print_and_write('Server maintenance')
                time.sleep(60)
                continue
            else:
                return

    def get_execute_order(self):
        try:
            result = self.bitflyer_api.getexecutions(product_code = 'FX_BTC_JPY',count = 1)
            #print(result['price'])
            return(float(result[0]['price']))
        except Exception:
            return (0)

    # judge if the time stamp in this hour
    def bf_timejudge(self, timestring):
        cur_time = time.gmtime()
        #time.sleep(10)
        #cur_time2 = time.gmtime()
        a = time.mktime(timestring)
        b = time.mktime(cur_time)
        tdelta = b - a
        return(tdelta)


    def get_orders(self, status = ''):
        #order = self.quoinex_api.get_orders()
        #order = self.quoinex_api.get_orders(status, limit)
        #ACTIVE CANCELED
        product = 'FX_BTC_JPY'
        if status != '':
            order = self.bitflyer_api.getparentorders(product_code=product, parent_order_state=status)
        else:
            order = self.bitflyer_api.getparentorders(product_code=product, count=30)
        return (order)


    def get_orderbyid(self, id):
        product = 'FX_BTC_JPY'
        i = 20
        while i > 0:
            try:
            #order = self.bitflyer_api.getparentorder(product_code=product, parent_order_acceptance_id=id)
                orders = self.get_orders()
                for i in orders:
                    if i['parent_order_acceptance_id'] == id:
                        return (i)
                print('order not find')
                return({})
            except Exception:
                print('Server is fucked off ,try again')
                time.sleep(20)
                i -= 1
                continue
        print('Try too many times, failed')
        return({})



    def judge_order(self, id):
        i = 20
        while i > 0:
            try:
                order = self.get_orderbyid(id)
                if order['parent_order_state'] == 'REJECTED':
                    predict.print_and_write('Order rejected')
                    return True
                else:
                    return False
            except Exception:
                time.sleep(5)
                print(Exception)
                print('Exception Try again')
                i -= 1
        predict.print_and_write('Try many times but no result, return False without confidence')
        return False

    def get_checkin_price(self):
        p = self.bitflyer_api.getpositions(product_code='FX_BTC_JPY')
        position0 = 0.0
        checkin_price = 0.0
        #time_diff = 0
        if isinstance(p, list):
            for i in p:
                #predict.print_and_write('check in price: %f' % (i['price']))
                if i['side'] == 'SELL':
                    position0 -= i['size']
                else:
                    position0 += i['size']

            for i in p:
                checkin_price += i['size']/abs(position0) * i['price']
            #predict.print_and_write('Check in price: %f, position: %f' % (checkin_price, position0))

            # for i in p:
            #     opentime = i['open_date']
            #     time_diff = self.bf_timejudge(opentime)
            #     break

        elif isinstance(p, dict) or len(p) == 0:
            predict.print_and_write('Position not exist')
        checkin_price = math.floor(checkin_price)
        return([checkin_price, position0])

    def get_current_price(self, number):
        d = 350
        while d > 0:
            try:
                trade_history = self.bitflyer_api.executions(product_code = 'FX_BTC_JPY', count = number)
                total_size = 0.0
                cur_price = 0.0
                for i in trade_history:
                    total_size += i['size']

                for i in trade_history:
                    cur_price += i['size']/total_size * i['price']

                if cur_price == 0.0:
                    time.sleep(0.1)
                    continue
                return(math.floor(cur_price))
            except Exception:
                print('Get price error ,try again')
                time.sleep(5)
                d -= 1
                continue
        print('Try too many times, failed')
        return 0.0

