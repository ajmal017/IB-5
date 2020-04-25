from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order


class IbOrder():

    def __init__(self):
        self.conn = Connection.create(port=7496, clientId=999)
        self.conn.connect()
        self.oid = 0

    def make_contract(self, symbol, sec_type, exch='SMART', prim_exchange='SMART', ccy='USD'):
        Contract.m_symbol = symbol
        Contract.m_secType = sec_type
        Contract.m_exchange = exch
        Contract.m_primaryExch = prim_exchange
        Contract.m_currency = ccy
        return Contract

    def make_order(self, action, quantity, price=None):
        if price is not None:
            order = Order()
            order.m_orderType = 'LMT'
            order.m_totalQuantity = quantity
            order.m_action = action
            order.m_lmtPrice = price
        else:
            order = Order()
            order.m_orderType = 'MKT'
            order.m_totalQuantity = quantity
            order.m_action = action
        return order

    def place_order(self, symbol, type, quantity, action):
        if quantity <= 0 or action.strip().upper() not in ['BUY', 'SELL']:
            raise AttributeError
        contract = self.make_contract(symbol, type)
        order = self.make_order(action.strip().upper(), quantity)
        self.conn.placeOrder(self.oid, contract, order)


from ib_insync import *
def IB_API():
    ib = IB()
    ib.connect(port=7496,clientId=999)
    contract = Forex('EURUSD')
    bars = ib.reqHistoricalData(contract, endDateTime='', durationStr='30 D',
                                barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)
    df = util.df(bars)
    print('a')
'''
def main():
    cid = 1
    conn = Connection.create(port=7496, clientId=999)
    conn.connect()
    cont = make_contract('TSLA', 'STK', 'SMART', 'SMART', 'USD')
    offer = make_order('BUY', 1)
    cid += 1
    oid = cid
    conn.placeOrder(oid, cont, offer)
    conn.disconnect()
'''

if __name__ == '__main__':
    IB_API()
