from tradersbot import TradersBot
import sys
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

C = 0.00004 # 1/25000
CASE_LENGTH = 450
CLOSE_OUT_MARGIN = 25 # when do we stop trading and balance our position
CURRENCY = 'USD'
DARK_TICKER = 'TRDRS.DARK'
INITIAL_CASH = 100000
ORDER_DELAY = 8
ORDER_LIMIT = 1000
ORDER_WAIT = 15 # how long to wait before evaluating the effect
LIT_TICKER = 'TRDRS.LIT'
MESSAGE_LIMIT = 25
POSITION_LIMIT = 5000

DARK_TRADING = True
# DARK_TRADING = False
POSITION_BALANCING = True
CANCEL_TRADES = True
# CANCEL_TRADES = False

cash = 100000
dark_advantage = 0.1 # ratio for DARK pricing
first_time = None
market_position_lit = 0
market_position_dark = 0
p0 = 200
position_lit = 0
position_dark = 0
price = 200
time_offset = 0 # for when it starts late

# TODO: use a more sophisticated probability model
# customers['Bob'] = {'full':0, 'half':5, 'random':1}
# the values are the number of times each possibility occurs
customers = {}
# maps customer name to a list for the probability of being each person
# 'Alice': ['random':p_r, 'half':p_h, 'full':p_f]
customer_identities = {}
pending_orders = []
# contains (ticker, trade_id, cancelled) = ('TRDRS.DARK', 0, False)
cancelled_trades = set()
recent_messages = []

def compute_valuation():
    net_position = position_lit + position_dark
    asset_value = net_position * price
    total_value = asset_value + cash
    return total_value

def update_probabilities():
    # For simplicity, we'll assume there are only 3 customers.
    # TODO: Fix this for any number of customers.
    names = list(customers.keys())
    probabilities = {}
    for key in customers:
        record = customers[key]
        total = record['random'] + record['half'] + record['full']
        if total == 0:
            probabilities[key] = [1/3, 1/3, 1/3]
        else:
            probabilities[key] = [record['random'] / total, record['half'] / total, record['full'] / total]
    p = probabilities; a = names[0]; b = names[1]; c = names[2]; r = 0; h = 1; f = 2
    customer_identities[a]['random'] = p[a][r] * (p[b][h]*p[c][f] + p[b][f]*p[c][h])
    customer_identities[a]['half'] = p[a][h] * (p[b][r]*p[c][f] + p[b][f]*p[c][r])
    customer_identities[a]['full'] = p[a][f] * (p[b][r]*p[c][h] + p[b][h]*p[c][r])
    customer_identities[b]['random'] = p[b][r] * (p[a][h]*p[c][f] + p[a][f]*p[c][h])
    customer_identities[b]['half'] = p[b][h] * (p[a][r]*p[c][f] + p[a][f]*p[c][r])
    customer_identities[b]['full'] = p[b][f] * (p[a][r]*p[c][h] + p[a][h]*p[c][r])
    customer_identities[c]['random'] = p[c][r] * (p[b][h]*p[a][f] + p[b][f]*p[a][h])
    customer_identities[c]['half'] = p[c][h] * (p[b][r]*p[a][f] + p[b][f]*p[a][r])
    customer_identities[c]['full'] = p[c][f] * (p[b][r]*p[a][h] + p[b][h]*p[a][r])
    

def ready_to_send():
    global recent_messages
    time_limit = get_time() - 1
    for i in range(len(recent_messages)):
        if recent_messages[i] >= time_limit:
            recent_messages = recent_messages[i:]
            break
    if len(recent_messages) < MESSAGE_LIMIT:
        recent_messages.append(get_time())
        return True
    return False

def get_time():
    if first_time is None:
        return time_offset
    delta = datetime.now() - first_time
    return delta.total_seconds() + time_offset

def process_orders(order):
    for pending in pending_orders:
        process_order(pending, order)

def process_order(pending_order, order):
    if not pending_order['sold'] and not is_closing_time():
        handle_pre_sale(pending_order, order)
        check_sold(pending_order)
    elif not pending_order['done'] and not is_closing_time():
        handle_post_sale(pending_order, order)
        check_done(pending_order)
    else:
        handle_clean_up(pending_order, order)

def handle_pre_sale(pending_order, order):
    reach_target_position(pending_order['target'], order)
    if DARK_TRADING:
        time_remaining = pending_order['sale_time'] - get_time()
        expected_position_lit = -position_dark + pending_order['size']
        market_price_guess = p0 - C*expected_position_lit
        # If customers are buying, increase the price
        # If customers are selling, decrease the price
        advantage_price = dark_advantage if pending_order['buy'] else -dark_advantage
        advantage_price *= price
        advantage_price += price
        if len(pending_order['orders']) != 0:
            pass
            # TODO: Check and reguess if you were wrong.
        elif pending_order['quantity'] != 0:
            attempted_price = advantage_price
            result = make_trade(pending_order['quantity'], order, ticker=DARK_TICKER, price=attempted_price)
            # [quantity, price, [list of ids]]
            pending_order['orders'].append(result + [[]])


def check_sold(pending_order):
    if get_time() > pending_order['sale_time']:
        pending_order['p0_at_sale'] = p0
        pending_order['sold'] = True

def handle_post_sale(pending_order, order):
    change_in_p0 = p0 - pending_order['p0_at_news']
    full = C * pending_order['size']
    half = full / 2
    margin = abs(full / 4)
    name = pending_order['source']
    if abs(change_in_p0 - full) <= margin:
        customers[name]['full'] += 1
        pending_order['p0_at_eval'] = p0
    elif abs(change_in_p0 - half) <= margin:
        customers[name]['half'] += 1
        pending_order['p0_at_eval'] = p0
    elif abs(change_in_p0) <= margin:
        if get_time() > pending_order['eval_time']:
            customers[name]['random'] += 1
            pending_order['p0_at_eval'] = p0
    elif get_time() > pending_order['eval_time']:
        pending_order['p0_at_eval'] = p0
    else:
        reach_target_position(pending_order['target'], order)
    

def check_done(pending_order):
    pending_order['done'] = pending_order['p0_at_eval'] is not None

def handle_clean_up(pending_order, order):
    if not CANCEL_TRADES:
        pending_orders.remove(pending_order)
        return
    for i in reversed(range(len(pending_order['orders']))):
        batch = pending_order['orders'][i]
        for j in reversed(range(len(batch[2]))):
            if ready_to_send():
                order.addCancel(DARK_TICKER, batch[2][j])
                batch[2].pop(j)
        if len(batch[2]) == 0:
            pending_order['orders'].pop(i)
    if len(pending_order['orders']) == 0:
        pending_orders.remove(pending_order)


def reach_target_position(target, order, ticker=LIT_TICKER, price=None):
    net_position = position_lit + position_dark
    if net_position != target:
        make_trade(target - net_position, order)

# Signed quantity, positive for buy, negative for sell
def make_trade(quantity, order, ticker=LIT_TICKER, price=None):
    magnitude = abs(quantity)
    num_orders = (magnitude // ORDER_LIMIT)
    if magnitude != num_orders*ORDER_LIMIT:
        num_orders += 1
    buy = quantity > 0
    quantity = int(magnitude / num_orders)
    successes = 0
    if buy:
        for i in range(int(num_orders)):
            if ready_to_send():
                if price is None:
                    order.addBuy(ticker, quantity)
                else:
                    order.addBuy(ticker, quantity, price=price)
                successes += 1
    else:
        for i in range(int(num_orders)):
            if ready_to_send():
                if price is None:
                    order.addSell(ticker, quantity)
                else:
                    order.addSell(ticker, quantity, price=price)
                successes += 1
    return [quantity * successes * (1 if buy else -1), price]

def is_closing_time():
    return CASE_LENGTH - get_time() < CLOSE_OUT_MARGIN

def close_out(order):
    if is_closing_time():
        reach_target_position(0, order)

def onAckRegister(msg, order):
    global POSITION_LIMIT, CURRENCY, CASE_LENGTH, INITIAL_CASH
    global time_offset, p0
    print(msg)
    if 'TRDRS' in msg['case_meta']['underlyings']:
        POSITION_LIMIT = msg['case_meta']['underlyings']['TRDRS']['limit']
    else:
        POSITION_LIMIT = msg['case_meta']['underlyings']['TRDRS.LIT']['limit']
    CURRENCY = msg['case_meta']['default_currency']
    CASE_LENGTH = msg['case_meta']['case_length']
    p0 = msg['case_meta']['securities']['TRDRS.LIT']['starting_price']
    time_offset = msg['elapsed_time']
    if time_offset == 0:
        INITIAL_CASH = msg['trader_state']['cash'][CURRENCY]
    for name in msg['case_meta']['news_sources']:
        customers[name] = {'full': 0, 'half': 0, 'random': 0}
        customer_identities[name] = {'full': 1/3, 'half': 1/3, 'random': 1/3}
    onTraderUpdate(msg, order)

def onMarketUpdate(msg, order):
    global first_time
    if first_time is None:
        first_time = datetime.now()
    state = msg['market_state']
    if state['ticker'] == 'TRDRS.LIT':
        global market_position_lit, price, p0
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
    process_orders(order)
    close_out(order)

def onTraderUpdate(msg, order):
    global cash, position_lit, position_dark, cancelled_trades
    state = msg['trader_state']
    cash = state['cash'][CURRENCY]
    position_lit = state['positions']['TRDRS.LIT']
    position_dark = state['positions']['TRDRS.DARK']
    open_order_ids = {int(state['open_orders'][order]['order_id']) for order in state['open_orders']}
    cancelled_trades = cancelled_trades & open_order_ids
    # for i in reversed(range(len(cancelled_trades))):
    #     if cancelled_trades[i][1] not in state['open_orders']:
    #         cancelled_trades.pop(i)
    for pending_order in pending_orders:
        for i in reversed(range(len(pending_order['orders']))):
            batch = pending_order['orders'][i]
            for j in reversed(range(len(batch[2]))):
                if batch[2][j] not in state['open_orders']:
                    batch[2].pop(j)
    pnl = (position_lit + position_dark) * price + cash - INITIAL_CASH
    time = int(get_time())
    print('\rLIT:{:<7} DARK:{:<7} CASH:{:<11.2f} PNL:{:<10.2f} T:{:<3}'.format(position_lit, position_dark, cash, pnl, time), end='\r')
    # print('\rLIT:\t%i\tDARK:\t%i\tCASH:\t%1.2f\tPNL:\t%1.2f' % (position_lit, position_dark, cash, pnl), end='\r')

def onTrade(msg, order):
    trades = set()
    for trade in msg['trades']:
        if trade['ticker'] == DARK_TICKER:
            trades.add(trade['trade_id'])
    for pending_order in pending_orders:
        for i in reversed(range(len(pending_order['orders']))):
            batch = pending_order['orders'][i]
            for j in reversed(range(len(batch[2]))):
                if batch[2][j] in trades:
                    batch[2].pop(j)

def onAckModifyOrders(msg, order):
    if 'cancels' in msg and CANCEL_TRADES:
        for trade_id in msg['cancels']:
            # remove successful cancels
            if not msg['cancels'][trade_id] and trade_id not in cancelled_trades:
                order.addCancel(DARK_TICKER, trade_id)
                cancelled_trades.add(int(trade_id))
            # trade = (DARK_TICKER, trade_id, False)
            # if trade not in cancelled_trades:
            #     trade = (LIT_TICKER, trade_id, False)
            #     if trade not in cancelled_trades:
            #         trade = (DARK_TICKER, trade_id, True)
            #         if trade not in cancelled_trades:
            #             trade = (LIT_TICKER, trade_id, True)
            #             if trade not in cancelled_trades:
            #                 continue
            # pending_trades.remove(trade)
            # if not msg['cancels'][trade_id]:
            #     # add back failed cancels
            #     pending_trades.add((trade[0], trade[1], False))

    for trade in msg['orders']:
        if trade['ticker'] == DARK_TICKER:
            price = trade['price']
            for pending_order in reversed(pending_orders):
                for batch in reversed(pending_order['orders']):
                    if price == batch[1]:
                        batch[2].append(str(trade['order_id']))
                        break
                else:
                    continue
                break

def onNews(msg, order):
    try:
        news = msg['news']
        headline = news['headline']
        buy = 'buy' in headline
        sell = 'sell' in headline
        source = news['source']
        news_time = news['time']
        size = news['body']
        if (not buy and not sell) or str(size) not in headline:
            print('Unable to parse headline: No buy or sell')
            return
        size = int(size) if buy else -int(size)
        target_position = POSITION_LIMIT if buy else -POSITION_LIMIT
        quantity = -2*POSITION_LIMIT if buy else 2*POSITION_LIMIT
        new_order = {'source': source,
                    'buy': buy,
                    'size': size,
                    'target': target_position,
                    'quantity': quantity,
                    'news_time': news_time,
                    'sale_time': news_time + ORDER_DELAY,
                    'eval_time': news_time + ORDER_WAIT,
                    'p0_at_news': p0,
                    'p0_at_sale': None,
                    'p0_at_eval': None,
                    'orders': [],
                    'sold': False,
                    'done': False}
        pending_orders.append(new_order)
    except:
        print('Unable to parse headline: Unknown error')

DEBUG = True
algo_bot = None
if len(sys.argv) >= 4:
    algo_bot = TradersBot(host=sys.argv[1], id=sys.argv[2], password=sys.argv[3])
    DEBUG = False
    CANCEL_TRADES = False
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