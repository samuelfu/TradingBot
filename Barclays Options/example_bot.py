'''
1. Exploit inconsistencies in implied volatility across different strike prices
2. Market make when spreads are large, without becoming overly exposed to risk
3. Hedge positions to reduce risk
'''
import tradersbot as tt
import numpy as np
from scipy import stats
t = tt.TradersBot(host='127.0.0.1', id='trader0', password='trader0')

# Keeps track of prices
SECURITIES = {}
# Keep track of time
startTime = ""

# Initializes the prices
def ack_register_method(msg, order):
	global SECURITIES
	global startTime
	security_dict = msg['case_meta']['securities']
	for security in security_dict.keys():
		if not(security_dict[security]['tradeable']):
			continue
		SECURITIES[security] = security_dict[security]['starting_price']

# Updates latest price
def market_update_method(msg, order):
	global SECURITIES
	SECURITIES[msg['market_state']['ticker']] = msg['market_state']['last_price']

# Buys or sells in a random quantity every time it gets an update
# You do not need to buy/sell here
def trader_update_method(msg, order):
	global SECURITIES
	positions = msg['trader_state']['positions']
	for security in positions.keys():
		if security == 'T100C':
			current_underlying_price = positions['TMXFUT']
			current_option_price = positions[security]
			IV = implied_vol('c', current_option_price, current_underlying_price, 100, 0, 1/12)
			predicted_price = bsm_price('c', IV, current_underlying_price, 100, 0, 1/12)
			# 1/12 will be updated to be a ticking time
			if predicted_price > current_option_price:
				order.addBuy(security, quantity=50,price=SECURITIES[security])
			else:
				order.addSell(security, quantity=50, price=SECURITIES[security])

			''' Original code
			if random.random() < 0.5:
				quant = 10
				order.addBuy(security, quantity=quant,price=SECURITIES[security])
			else:
				quant = 10
				order.addSell(security, quantity=quant,price=SECURITIES[security])
			'''

# Black-Scholes formula.
# Current price of the underlying (the spot price) S
# Strike price K
# Risk-free interest rate r = 0
# Volatility sigma
# expiration time T - current time t = t
# https://www.quantconnect.com/tutorials/introduction-to-options/historical-volatility-and-implied-volatility

def bsm_price(option_type, sigma, s, k, r, T):
    # calculate the bsm price of European call and put options
    sigma = float(sigma)
    d1 = (np.log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'c':
        price = np.exp(-r*T) * (s * np.exp(r*T) * stats.norm.cdf(d1) - k *  stats.norm.cdf(d2))
        return price
    elif option_type == 'p':
        price = np.exp(-r*T) * (k * stats.norm.cdf(-d2) - s * np.exp(r*T) *  stats.norm.cdf(-d1))
        return price

def implied_vol(option_type, option_price, s, k, r, T):
    # apply bisection method to get the implied volatility by solving the BSM function
    precision = 0.00001
    upper_vol = 500.0
    max_vol = 500.0
    min_vol = 0.0001
    lower_vol = 0.0001
    iteration = 0

    while 1:
        iteration +=1
        mid_vol = (upper_vol + lower_vol)/2.0
        price = bsm_price(option_type, mid_vol, s, k, r, T)
        if option_type == 'c':
            lower_price = bsm_price(option_type, lower_vol, s, k, r, T)
            if (lower_price - option_price) * (price - option_price) > 0:
                lower_vol = mid_vol
            else:
                upper_vol = mid_vol
            if abs(price - option_price) < precision:
                break
            if mid_vol > max_vol - 5 :
                mid_vol = 0.000001
                break

        elif option_type == 'p':
            upper_price = bsm_price(option_type, upper_vol, s, k, r, T)
            if (upper_price - option_price) * (price - option_price) > 0:
                upper_vol = mid_vol
            else:
                lower_vol = mid_vol
            if abs(price - option_price) < precision:
                break
        if iteration > 50:
            break
    return mid_vol


t.onAckRegister = ack_register_method
t.onMarketUpdate = market_update_method
t.onTraderUpdate = trader_update_method
#t.onTrade = trade_method
#t.onAckModifyOrders = ack_modify_orders_method
#t.onNews = news_method
t.run()