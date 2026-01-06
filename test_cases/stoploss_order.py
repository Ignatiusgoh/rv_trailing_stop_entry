import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   

from dotenv import load_dotenv

load_dotenv()

### TESTING PLACING MARKET ORDER ###

trade = BinanceFuturesTrader()

try: 
    response = trade.set_stop_loss(symbol="SOLUSDT", side="SELL", stop_price=135)
    print(response)
except Exception as e:
    print(f"Error: {e}")
