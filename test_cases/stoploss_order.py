import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   
from utils.supabase_client import log_into_supabase
from candle import TestCandle
from dotenv import load_dotenv

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
order_table_name = os.getenv("ORDER_TABLE")
supabase_api_key = os.getenv("SUPABASE_API_KEY")
supbase_jwt = os.getenv("SUPABASE_JWT")
### TESTING PLACING MARKET ORDER ###

trade = BinanceFuturesTrader()

try: 
    stoploss_order = trade.set_stop_loss(symbol="SOLUSDT", side="SELL", stop_price=120)
    print(stoploss_order)
    # Algo Order API returns 'algoId' or 'clientAlgoId', not 'orderId'
    stoploss_order_id = stoploss_order.get('algoId') or stoploss_order.get('clientAlgoId') or stoploss_order.get('orderId')
    print(f"Stop loss order ID: {stoploss_order_id}")
    
test_candle = TestCandle()
try: 
    res = test_candle.test_insert_sl()
    print(res)
except Exception as e:
    print(f"Error: {e}")

except Exception as e:
    print(f"Error: {e}")
