import time
import predict
import json
import websocket
import tradebf_basic



class Alert_trading(tradebf_basic.Trade_basic):
    secret = 'RMihWn21BWxgDbM8YZ-f2DGFrWJH4GV6Dslf7k5nyr'
    url = 'wss://pushstream.tradingview.com/message-pipe-ws/private_' + secret

    amount_pivot = 0.0
    position_pivot = 0.0
    enter_price = -100
    #trail order parameter
    testFlag = True

    def __init__(self):
        tradebf_basic.Trade_basic.__init__(self)
        print('Alert sys loaded')
        self.read_ini()
        self.set_vals()


    def on_message(self, ws, message):
        message = json.loads(message)
        if self.secret in message['channel']:
            if message['text']['channel'] == 'alert':
                content = json.loads(message['text']['content'])
                if content['m'] == 'event':
                    self.process_msg(content['p']['desc'])


    def print_position(self):
        predict.print_and_write('Pivot : %.2f'%(float(self.position_pivot)))

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

    def process_msg(self, str):
        self.get_vals()

        if (str == 'pivot_short' or str == 'Repeat_short') and self.position_pivot >= 0.0:
        #if self.testFlag:
            print("msg: %s is processed" % str)
            self.amount_pivot = self.decide_trade_amount()
            trade_amount = self.amount_pivot + self.position_pivot

            self.position_pivot = self.position_pivot - trade_amount
            self.enter_price = self.get_current_price(50)
            self.print_position()
            order = self.trade_market('sell', trade_amount, self.enter_price)
            predict.print_and_write(order)
            self.set_vals()
            self.write_ini()
            return (True)
        elif (str == 'pivot_long' or str == 'Repeat_long') and self.position_pivot <= 0.0:
            print("msg: %s is processed" % str)
            self.amount_pivot = self.decide_trade_amount()
            trade_amount = self.amount_pivot - self.position_pivot

            self.position_pivot = self.position_pivot + trade_amount
            self.enter_price = self.get_current_price(50)
            self.print_position()
            order = self.trade_market('buy', trade_amount, self.enter_price)
            predict.print_and_write(order)
            self.set_vals()
            self.write_ini()
            return (True)
        else:
            print("msg: %s is ignored." % str)
            pass

    def run(self):
        ws = websocket.WebSocketApp(self.url, on_message=self.on_message)
        while 1:
            try:
                ws.run_forever()
                time.sleep(1)
            except Exception:
                print(Exception)
                time.sleep(1)
                continue

if __name__ == '__main__':
    autoTrading = Alert_trading()
    #autoTrading.process_msg('pivot_short')
    #autoTrading.process_msg('pivot_long')
    autoTrading.run()
