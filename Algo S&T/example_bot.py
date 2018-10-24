from tradersbot import *
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

#Initialize variables: positions, expectations, future customer orders, etc
position_limit = 5000
case_length = 450
cash = 0
position_lit = 0
position_dark = 0
time = 0
topBid = 0
topAsk = 0
#etc etc

def register(msg, TradersOrder):
    #Set case information
    pass

def update_market(TradersOrder):
    #Update market information
    pass

def update_trader(TradersOrder):
    #Update positions
    pass

def update_trade(msg, TradersOrder):
    #Update trade information
    pass

def update_order(msg, TradersOrder):
    #Update order information
    pass

def update_news(msg, TradersOrder):
    #Update news information
    pass

def process():
    #Do stuff to trade
    pass

t = TradersBot('127.0.0.1', 'trader0', 'trader0')

t.onAckRegister = register
t.onMarketUpdate = update_market
t.onTraderUpdate = update_trader
t.onTrade = update_trade
t.onAckModifyOrders = update_order
t.onNews = update_news

t.run()
