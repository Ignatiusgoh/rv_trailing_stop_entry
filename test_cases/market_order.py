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
    set_leverage = trade.set_leverage(symbol="SOLUSDT", leverage=20)
    print(set_leverage)
except Exception as e:
    print(f"Error: {e}")
try:
    response = trade.place_market_order(symbol="SOLUSDT", side="BUY", quantity=465.12)
    print(response)
except Exception as e:
    print(f"Error: {e}")    