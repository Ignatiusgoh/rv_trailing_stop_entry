import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   
from candle import TestCandle
import time 
from utils.binancehelpers import entry_price

from dotenv import load_dotenv
import time

load_dotenv()

### TESTING GETTING ENTRY PRICE ###
market_in_order_id = "195785622689"
trade = BinanceFuturesTrader()
try:
    actual_entry_price = entry_price(market_in_order_id)    
    print(actual_entry_price)
except Exception as e:
    print(f"Error: {e}")