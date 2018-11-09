import tradersbot as tt
import random

t = tt.TradersBot(host='127.0.0.1', id='trader0', password='trader0')

# Keeps track of prices
SECURITIES = {}

# Initializes the prices
def ack_register_method(msg, order):
	global SECURITIES
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
		if random.random() < 0.5:
			quant = 10*random.randint(1, 10)
			order.addBuy(security, quantity=quant,price=SECURITIES[security])
		else:
			quant = 10*random.randint(1, 10)
			order.addSell(security, quantity=quant,price=SECURITIES[security])

###############################################
#### You can add more of these if you want ####
###############################################

t.onAckRegister = ack_register_method
t.onMarketUpdate = market_update_method
t.onTraderUpdate = trader_update_method
#t.onTrade = trade_method
#t.onAckModifyOrders = ack_modify_orders_method
#t.onNews = news_method
t.run()