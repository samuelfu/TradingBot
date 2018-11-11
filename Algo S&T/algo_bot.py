from tradersbot import TradersBot
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class AlgoBot(TradersBot):
    #Initialize variables: positions, expectations, future customer orders, etc
    POSITION_LIMIT = 5000
    CASE_LENGTH = 450
    CURRENCY = 'USD'
    ORDER_DELAY = 8

    cash = 0
    market_position_lit = 0
    market_position_dark = 0
    position_lit = 0
    position_dark = 0
    first_time = None
    time = 0
    topBid = 0
    topAsk = 0
    c = 0.00004
    customers = {}
    # contains (price, time) where price is an estimate for p_0
    lit_price_history = []
    pending_order = None
    existing_trades = []

    def onAckRegister(self, msg, order):
        print('reg')
        self.POSITION_LIMIT = msg['case_meta']['underlyings']['TRDRS']['limit']
        self.CURRENCY = msg['case_meta']['default_currency']
        self.CASE_LENGTH = msg['case_meta']['case_length']
        self.cash = msg['trader_state']['cash'][self.CURRENCY]
        self.time = msg['elapsed_time']
        customers = {name for name in msg['case_meta']['news_sources']}
        position_lit = msg['trader_state']['positions']['TRDRS.LIT']
        position_dark = msg['trader_state']['positions']['TRDRS.DARK']
    
    def onMarketUpdate(self, msg, order):
        print('market')
        if self.first_time is None:
            self.first_time = datetime.now()
        delta = datetime.now() - self.first_time
        self.time = delta.total_seconds()
        print(time)
        lit_price = msg['market_state']['last_price']

    def onTraderUpdate(self, msg, order):
        # Looks like this never runs
        print(msg)
        order.addBuy('TRDRS.LIT', quantity=100)
        state = msg['trader_state']
        self.cash = state['cash'][self.CURRENCY]
        print(msg)
        # self.position_lit = state['positions']

    def onTrade(self, msg, order):
        order.addBuy('TRDRS.LIT', quantity=100)
        for trade in msg['trades']:
            if trade['ticker'] == 'TRDRS.LIT':
                self.market_position_lit += trade['quantity'] * (-1 if trade['buy'] else 1)
            else:
                self.market_position_dark += trade['quantity'] * (-1 if trade['buy'] else 1)

    def onAckModifyOrders(self, msg, order):
        pass

    def onNews(self, msg, order):
        try:
            news = msg['news']
            headline = news['headline']
            buy = 'buy' in headline
            sell = 'sell' in headline
            source = news['source']
            news_time = news['time']
            quantity = news['body']
            if (not buy and not sell) or str(quantity) not in headline:
                print('Unable to parse headline')
                return
            quantity = int(quantity)
            new_order = {'source': source,
                        'buy': buy,
                        'news_time': news_time}
        except:
            print('Unable to parse headline')
#etc etc
{'message_type': 'ACK REGISTER',
'case_meta':
    {'case_length': 450,
    'speedup': 1,
    'default_currency':'USD',
    'securities': {
        'TRDRS.LIT': {
            'dark': False, 
            'tradeable': True, 
            'invisible': False, 
            'starting_price': 200, 
            'underlyings': {'TRDRS': 1}, 
            'precision': 2}, 
        'TRDRS.DARK': {
            'dark': True, 
            'tradeable': True, 
            'invisible': False, 
            'starting_price': 200, 
            'underlyings': {'TRDRS': 1}, 
            'precision': 2}}, 
    'underlyings': {
        'TRDRS': {
            'name': 'TRDRS', 
            'limit': 5000}}, 
    'news_sources': 
        {'Carol': {
            'paid': False, 
            'can_unsubscribe': False}, 
        'Alice': {
            'paid': False, 
            'can_unsubscribe': False}, 
        'Bob': {
            'paid': False, 
            'can_unsubscribe': False}}, 
    'currencies': {
        'USD': {'name': 'USD', 'limit': 0}}}, 
'elapsed_time': 3, 
'market_states': {
    'TRDRS.LIT': {
        'ticker': 'TRDRS.LIT', 
        'bids': {'199.80': 365, '199.85': 268, '199.83': 329, '199.82': 347, '199.86': 190}, 
        'asks': {'200.03': 199, '200.04': 303, '200.02': 222, '200.01': 108, '200.05': 329, '200.06': 347, '200.08': 365, '200.07': 359}, 
        'last_price': 199.86, 
        'time': '2018-11-05T20:39:00.053214849-05:00'}, 
    'TRDRS.DARK': {'ticker': 'TRDRS.DARK', 'bids': {}, 'asks': {}, 'last_price': 200, 'time': '2018-11-05T20:39:00.053215656-05:00'}}, 
'trader_state': {
    'trader_id': 'trader0', 
    'cash': {'USD': 100000}, 
    'positions': {'TRDRS.LIT': 0, 'TRDRS.DARK': 0}, 
    'open_orders': {}, 
    'pnl': {'USD': 0}, 'default_pnl': 0, 'time': '2018-11-05T20:39:00.053197152-05:00', 'total_fees': 0, 'total_fines': 0, 'total_rebates': 0, 'subscriptions': {}}}

algo_bot = None
if len(sys.argv) >= 4:
    algo_bot = AlgoBot(host=sys.argv[1], id=sys.argv[2], password=sys.argv[3])
else:
    algo_bot = AlgoBot('127.0.0.1', 'trader0', 'trader0')
algo_bot.run()