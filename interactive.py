"""
a template for any strategy
"""
import time
from observer import *
from HydraQuoteManager import HydraQuoteManager
from HydraOrderFactory import HydraOrderFactory
import threading
from HydraOrder import *
from HydraPositionUpdater import HydraPositionUpdater
from Positions import Positions
import google_sheet_dtp as gs


class InteractiveStrategy(object):

    def __init__(self, quoteManger, executionManager):
        self.qm = quoteManger
        self.em = executionManager
        self.of = HydraOrderFactory()
        self.quotes = {}
        self.quotes_lock = threading.Lock()
        self.open_orders = {}
        self.open_orders_lock = threading.Lock()
        self.closed_orders = {}
        self.closed_orders_lock = threading.Lock()
        self.positions = Positions()
        self.google_sheet = 0

        # ----- observers -----
        self.bidObserver = InteractiveStrategy.BidObserver(self)
        self.askObserver = InteractiveStrategy.AskObserver(self)
        self.lastObserver = InteractiveStrategy.LastObserver(self)
        self.orderStatusObserver = InteractiveStrategy.OrderStatusObserver(self)
        self.timer_thread = 0
        self.run = False

    def start(self):
        if self.run: return
        self.run = True

        self.timer_thread = threading.Thread(target=self.on_second)
        self.timer_thread.start()

        while 1:
            try:
                ui = raw_input('interactive>')

                if ui[:4].upper() == 'ECHO':
                    print ui[4:]

                elif ui[:3].upper() == 'BUY':
                    o = self.of.buy(ui)
                    self.send_order(o)

                elif ui[:4].upper() == 'SELL':
                    o = self.of.sell(ui)
                    self.send_order(o)

                elif ui.upper() == 'PRINT OPEN ORDERS':
                    print len(self.open_orders)
                    self.print_open_orders()

                elif ui.upper() == 'PRINT CLOSED ORDERS':
                    print len(self.closed_orders)
                    self.print_closed_orders()

                elif ui.upper() == 'CANCEL OPEN ORDERS':
                    for key, value in self.open_orders.iteritems():
                        self.em.cancel_order(value)

                elif ui.upper() == 'QUIT' or ui.upper() =='Q':
                    print 'Breaking out of interactive.'
                    break

                elif ui.upper() == 'LOAD SHEET':
                    try:
                        self.google_sheet = gs.GoogleSheetDailyTradingProcedure()
                        print 'wait a moment . . . '
                        self.google_sheet.load_sheet()
                        print 'sheet loaded'
                    except:
                        print 'problem loading sheet'

                elif ui.upper() == 'PRINT SHEET':
                    if self.google_sheet:
                        for row in self.google_sheet.sheet:
                            print row
                    else:
                        print 'Load sheet first. (cmd = load sheet)'

                elif ui.upper()[:9] == 'PRINT ROW':
                    if self.google_sheet:
                        tokens = ui.split(' ')
                        print self.google_sheet.sheet[int(tokens[2]) - 1]
                    else:
                        print 'Load sheet first. (cmd = load sheet)'


                elif ui.upper() == 'POSITIONS':
                    if self.google_sheet:
                        print self.positions
                    else:
                        print 'Load sheet first. (cmd = load sheet)'


                elif ui.upper()[:10] == 'SUBMIT ROW':
                    self.submit_row(int(ui.split(' ')[2])-1)

                elif ui.upper() == 'SUBMIT ALL':
                    if self.google_sheet.sheet:
                        i = -1
                        for _ in self.google_sheet.sheet:
                            i += 1
                            if i < 2: continue
                            strategy = self.google_sheet.sheet[i][0]
                            self.submit_row(i)
                    else:
                        pass

                else:
                    print 'Command not understood.'


            except Exception as e:
                print 'Error in interactive:'
                print e

    def submit_row(self, r):
        try:
            if self.google_sheet:
                row = self.google_sheet.sheet[r]
                print row
                strategy = row[0]
                account = row[1].upper()
                symbol = row[2].split()[0].upper()
                if symbol == '': return
                if row[4] == '':
                    print "Row doesn't have quantity. Enter quantity and reload sheet."
                    return
                quantity = int(row[4])
                side = 'buy' if (row[3].upper() == 'LONG' or row[3].upper() == 'BUY') else 'sell'
                if side == 'sell': quantity *= -1
                type = row[6].upper()
                if row[7] == '':
                    price = 0
                else:
                    price = float(row[7][1:]) if row[7][0] == '$' else float(row[7])
                trade_date = row[8]
                note = row[11]
                note2 = row[12]

                print strategy, account, symbol, quantity, side, type, price, trade_date, note, note2
                o = 0
                if type == 'MOO':
                    o = self.of.generate_opg_market_order(quantity, symbol, account)
                elif type == 'LOO':
                    o = self.of.generate_opg_limit_order(quantity, symbol, price, account)
                elif type == 'MOC':
                    o = self.of.generate_moc_market_order(quantity, symbol, account)
                elif type == 'LIMIT' or type == 'LMT':
                    o = self.of.generate_limit_order(quantity, symbol, price, account)
                inp = raw_input('{} {} {} {} {} in {}? (y/n)'.format(side, abs(quantity), symbol, price, type, account))
                if inp == 'y':
                    self.send_order(o)
                else:
                    print 'order not submitted: {}'.format(o)
            else:
                print 'Load sheet first. (cmd = load sheet)'
        except Exception as e:
            print 'row {} failed to submit: {}'.format(r + 1, e)

    def stop(self):
        self.run = False
        with self.quotes_lock:
            for key, val in self.quotes.iteritems():
                self.qm.stop_quote_stream(val.symbol)

        with self.open_orders_lock:
            for key, val in self.open_orders.iteritems():
                self.em.cancel_order(val)

        if self.timer_thread:
            self.timer_thread.join()

        i = 0
        while len(self.open_orders) > 0:
            if i == 5: break
            time.sleep(1)
            i += 1

    def add_quote(self, symbol):
        if symbol in self.quotes: return
        q = self.qm.start_quote_stream(symbol)

        with self.quotes_lock:
            self.quotes[symbol] = q

        q.askNotifier.addObserver(self.askObserver)
        q.bidNotifier.addObserver(self.bidObserver)
        q.lastNotifier.addObserver(self.lastObserver)

    def send_order(self, o):
        with self.open_orders_lock:
            self.open_orders[o.parent_id] = o

        o.statusChangeNotifier.addObserver(self.orderStatusObserver)
        self.em.send_order(o)

    def move_order_to_closed_list(self, ord):
        with self.open_orders_lock:
            try:
                o = self.open_orders[ord.parent_id]
                if o != None:
                    self.closed_orders[o.parent_id] = o
                    del self.open_orders[ord.parent_id]
            except KeyError:
                pass


    @staticmethod
    def print_orders(ords, lock):
        with lock:
            i = 0
            for key, ord in ords.iteritems():
                print '{}. {} {} {} {} @{} exec_qty={} stat={} leaves={}\n'.format(
                    i,
                    ord.account,
                    ord.symbol,
                    ord.side,
                    ord.quantity,
                    ord.order_price,
                    ord.executed_quantity,
                    ord.status,
                    ord.leaves_qty
                )
                i += 1

    def print_open_orders(self):
        InteractiveStrategy.print_orders(self.open_orders, self.open_orders_lock)

    def print_closed_orders(self):
        InteractiveStrategy.print_orders(self.closed_orders, self.closed_orders_lock)

    def on_ask(self, quote):
        pass

    def on_bid(self, quote):
        pass

    def on_last(self, quote):
        pass

    def on_order_status(self, ord_msg_tuple):
        # print ord
        ord = ord_msg_tuple[0]
        msg = ord_msg_tuple[1]
        if ord.status == order_status_type.canceled:
            self.move_order_to_closed_list(ord)
        elif ord.status == order_status_type.partial_open:
            p = self.positions.get_or_create(ord.symbol)
            HydraPositionUpdater.UpdatePosition(p, msg)
        elif ord.status == order_status_type.executed:
            p = self.positions.get_or_create(ord.symbol)
            HydraPositionUpdater.UpdatePosition(p, msg)
            self.move_order_to_closed_list(ord)

    def on_second(self):
        while 1:
            # on second code
            if not self.run:
                break
            time.sleep(1)

    class AskObserver(Observer):
        def __init__(self, outer):
            self.outer = outer

        def update(self, arg):
            self.outer.on_ask(arg)

    class BidObserver(Observer):
        def __init__(self, outer):
            self.outer = outer

        def update(self, arg):
            self.outer.on_bid(arg)

    class LastObserver(Observer):
        def __init__(self, outer):
            self.outer = outer

        def update(self, arg):
            self.outer.on_last(arg)

    class OrderStatusObserver(Observer):
        def __init__(self, outer):
            self.outer = outer

        def update(self, arg):
            self.outer.on_order_status(arg)

