from tradersbot import TradersBot
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

#Initialize variables: positions, expectations, future customer orders, etc
POSITION_LIMIT = 5000
CASE_LENGTH = 450
CURRENCY = 'USD'
ORDER_DELAY = 8
ORDER_WAIT = 15 # how long to wait before evaluating the effect
C = 0.00004
MESSAGE_LIMIT = 25

p0 = 200
cash = 100000
price = 200
market_position_lit = 0
market_position_dark = 0
position_lit = 0
position_dark = 0
first_time = None
time = 0
time_offset = 0 # for when it starts late
topBid = 0
topAsk = 0
# TODO: use a more sophisticated probability model
# customers['Bob'] = {'full':0, 'half':5, 'random':1}
# the values are the number of times each possibility occurs
customers = {}
pending_orders = []
# contains (ticker, trade_id, cancelled) = ('TRDRS.DARK', 0, False)
pending_trades = set()
recent_messages = []

def readyToSend():
    global MESSAGE_LIMIT, recent_messages, time
    updateTime()
    time_limit = time - 1
    for i in range(len(recent_messages)):
        if recent_messages[i] >= time_limit:
            recent_messages = recent_messages[i:]
    if len(recent_messages) < MESSAGE_LIMIT:
        recent_messages.append(time)
        return True
    return False

def updateTime():
    global first_time, time, time_offset
    if first_time is None:
        first_time = datetime.now()
    delta = datetime.now() - first_time
    time = delta.total_seconds() + time_offset

def processOrders(order):
    global pending_orders
    for pending in pending_orders:
        processOrder(pending, order)

def processOrder(pending_order, order):
    global time, p0, customers
    if pending_order is None:
        return
    print('bo')
    print(pending_order)
    if pending_order['p0_at_sale'] is None:
        print('moo')
        if time >= pending_order['sale_time']:
            print('1)')
            global market_position_dark
            market_position_dark += pending_order['quantity']
            pending_order['p0_at_sale'] = p0
        elif len(pending_trades) == 0:
            print('2')
            # TODO: Add support for using multiple trades of DARK
            # You'll need to track how much you already sent and what you expect to reach
            global customers
            customer = customers[pending_order['source']]
            trustworthiness = customer['full'] + customer['half'] - customer['random']
            # TODO: consider adding equality
            if trustworthiness >= 0:
                global POSITION_LIMIT
                global position_lit, position_dark, cash, price
                quantity = pending_order['quantity']
                # follow your guess
                if pending_order['buy']:
                    # p0 might go up
                    # buy LIT, sell DARK
                    buy_quantity = POSITION_LIMIT - position_lit - position_dark
                    affordable = cash / price
                    buy_quantity = int(min(quantity, buy_quantity, affordable))
                    sell_quantity = int(position_lit + position_dark)
                    difference = 0
                    if buy_quantity >= 100 and readyToSend():
                        difference = max(buy_quantity - 1000, 0)
                        order.addBuy('TRDRS.LIT', buy_quantity - difference)
                        sell_quantity = int(buy_quantity + position_lit + position_dark)
                    # TODO: guess the price in a better way
                    if sell_quantity >= 1000 and readyToSend():
                        order.addSell('TRDRS.DARK', sell_quantity - difference, price=price)
                else:
                    # expecting p0 to go down
                    # sell LIT, buy DARK
                    sell_quantity = int(position_lit + position_dark)
                    buy_quantity = POSITION_LIMIT - position_lit - position_dark
                    affordable = cash / price
                    # TODO: compute price in a better way
                    buy_quantity = int(min(abs(quantity), affordable, buy_quantity))
                    difference = 0
                    if sell_quantity >= 100 and readyToSend():
                        difference = max(sell_quantity - 1000, 0)
                        order.addSell('TRDRS.LIT', sell_quantity - difference)
                    if buy_quantity >= 1000 and readyToSend():
                        order.addBuy('TRDRS.DARK', buy_quantity - difference, price=price)
            else:
                # we think it's random
                pass
        else:
            print('jump')
    elif pending_order['p0_at_eval'] is None and time >= pending_order['eval_time']:
        print('3')
        global pending_orders, C
        pending_order['p0_at_eval'] = p0
        change_in_p0 = p0 - pending_order['p0_at_news']
        full = C * pending_order['quantity']
        half = full / 2
        margin = full / 4
        name = pending_order['source']
        if abs(change_in_p0 - full) <= margin:
            customers[name]['full'] += 1
        elif abs(change_in_p0 - half) <= margin:
            customers[name]['half'] += 1
        else:
            customers[name]['random'] += 1
        cancelTrades(order)
        pending_orders = pending_orders[1:]
    else:
        print('no')

def cancelTrades(order):
    global pending_trades
    for pending in pending_trades:
        if not pending[2] and readyToSend():
            order.addCancel(pending[0], pending[1])
            pending_trades.remove(pending)
            pending_trades.add((pending[0], pending[1], True))

def onAckRegister(msg, order):
    print('reg')
    global POSITION_LIMIT, CURRENCY, CASE_LENGTH
    global time, p0
    POSITION_LIMIT = msg['case_meta']['underlyings']['TRDRS']['limit']
    CURRENCY = msg['case_meta']['default_currency']
    CASE_LENGTH = msg['case_meta']['case_length']
    p0 = msg['case_meta']['securities']['TRDRS.LIT']['starting_price']
    time = msg['elapsed_time']
    if time != 0:
        global time_offset
        time_offset = msg['elapsed_time']
        first_time = datetime.now() - timedelta(seconds=time)
    for name in msg['case_meta']['news_sources']:
        customers[name] = {'full': 0, 'half': 0, 'random': 0}
    onTraderUpdate(msg, order)

def onMarketUpdate(msg, order):
    print('mark')
    updateTime()
    state = msg['market_state']
    if state['ticker'] == 'TRDRS.LIT':
        global market_position_lit, price, p0, C
        price = state['last_price']
        delta = 0
        bids = [state['bids'][p] for p in state['bids'] if float(p) >= price]
        asks = [state['asks'][p] for p in state['asks'] if float(p) <= price]
        delta = sum(bids) - sum(asks)
        market_position_lit -= delta
        p0 = price + C * market_position_lit
    else:
        if len(state['bids']) != 0:
            print('Bids', state['bids'])
        if len(state['asks']) != 0:
            print('Asks', state['asks'])
    processOrders(order)

def onTraderUpdate(msg, order):
    print('trader')
    global CURRENCY
    global cash, position_lit, position_dark
    state = msg['trader_state']
    cash = state['cash'][CURRENCY]
    position_lit = state['positions']['TRDRS.LIT']
    position_dark = state['positions']['TRDRS.DARK']
    print(state['open_orders'])
    print('PNL:', state['pnl'][CURRENCY])

def onTrade(msg, order):
    print('trade')
    global pending_trades
    for trade in msg['trades']:
        pending_trades.discard((trade['ticker'], trade['trade_id'], False))

def onAckModifyOrders(msg, order):
    print('mod')
    global pending_trades
    if 'cancels' in msg:
        for trade_id in msg['cancels']:
            # remove successful cancels
            trade = ('TRDRS.DARK', trade_id, True)
            if ('TRDRS.DARK', trade_id, True) not in pending_trades:
                trade = ('TRDRS.LIT', trade_id, True)
            pending_trades.remove(trade)
            if not msg['cancels'][trade_id]:
                # add back failed cancels
                pending_trades.add((trade[0], trade[1], False))

    for trade in msg['orders']:
        order = (trade['ticker'], str(trade['order_id']), False)
        # add orders we just sent in
        pending_trades.add(order)

def onNews(msg, order):
    print('news')
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
        quantity = int(quantity) * (1 if buy else -1)
        global ORDER_DELAY
        global pending_orders, p0
        new_order = {'source': source,
                    'buy': buy,
                    'quantity': quantity,
                    'news_time': news_time,
                    'sale_time': news_time + ORDER_DELAY,
                    'eval_time': news_time + ORDER_WAIT,
                    'p0_at_news': p0,
                    'p0_at_sale': None,
                    'p0_at_eval': None}
        pending_orders.append(new_order)
    except:
        print('Unable to parse headline')

DEBUG = False
algo_bot = None
if len(sys.argv) >= 4:
    algo_bot = TradersBot(host=sys.argv[1], id=sys.argv[2], password=sys.argv[3])
    DEBUG = False
else:
    algo_bot = TradersBot('127.0.0.1', 'trader0', 'trader0')
algo_bot.onAckRegister = onAckRegister
algo_bot.onMarketUpdate = onMarketUpdate
algo_bot.onTraderUpdate = onTraderUpdate
algo_bot.onTrade = onTrade
algo_bot.onAckModifyOrders = onAckModifyOrders
algo_bot.onNews = onNews

if not DEBUG:
    def f(*args):
        return None
    print = f

algo_bot.run()