from google_api import *


class GoogleSheetDailyTradingProcedure(object):
    def __init__(self):
        # TODO need order factory and order sender
        self.sheet = 0
        pass

    def process_row(self, row, i=0):
        if (len(row) >= 9):
            strategy = str(row[0]).upper().strip()
            if strategy == 'STRATEGY': return  # title row

            account = str(row[1]).upper().strip()
            symbol = str(row[2]).split(' ')[0].upper().strip()
            side = str(row[3]).upper().strip()
            shares = str(row[4]).strip()
            dollar_value = str(row[5]).strip()
            order_type = str(row[6]).upper().strip()
            limit_price = str(row[7])
            order_date = str(row[8])
            exit_strategy = ''
            if (len(row)) >= 11:
                exit_strategy = str(row[10])

            print '{}. strat:{} acct:{} symb:{} side:{} shrs:{} ${} {}k type:{} dd:{} exit:{}'.format(
                i, strategy, account, symbol, side, shares, limit_price[1:], dollar_value, order_type, order_date,
                exit_strategy
            )

            if strategy == 'SENTIMENT':
                pass
            elif strategy == 'SECONDARY':
                pass
            elif strategy == 'INDEX MOME':
                pass
            elif strategy == 'CLE':
                pass
            elif strategy == 'INDEX ARB':
                pass
            elif strategy == 'LOCK-UP':
                pass
            elif strategy == 'IPO':
                pass
            elif strategy == 'RSI':
                pass
            elif strategy == 'BUYBACK':
                pass
            elif strategy == 'JAP CROSS':
                pass
            elif strategy == 'CORP ACTION':
                pass
            elif strategy == 'Tax':
                pass

    def process_sheet(self, confirm=True):
        sheet = get_sheet()  # using the api code
        i = 1
        for row in sheet:
            i += 1
            self.process_row(row, i)

    def get_row(self, row_number):
        sheet = get_sheet()
        try:
            return sheet[row_number + 1]
        except:
            return None

    def print_row(self, row_number):
        row = self.get_row(row_number)
        print row

    def load_sheet(self):
        self.sheet = get_sheet()
