import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   
from candle import TestCandle
import time 

from dotenv import load_dotenv

load_dotenv()

### TESTING PLACING MARKET ORDER ###

trade = BinanceFuturesTrader()

# try: 
#     set_leverage = trade.set_leverage(symbol="SOLUSDT", leverage=30)
#     print(set_leverage)
# except Exception as e:
#     print(f"Error: {e}")
try:
    response = trade.place_market_order(symbol="SOLUSDT", side="BUY", quantity=3)
    print(response)
    market_in_order_id = response['orderId']
except Exception as e:
    print(f"Error: {e}")

test_candle = TestCandle()
try: 
    res = test_candle.test_insert_mo(market_in_order_id)
    print(res)
except Exception as e:
    print(f"Error: {e}")


### TESTING CLOSE ALL POSITIONS ###

def close_all_positions():
    """Close all open positions on Binance"""
    try:
        print("\n=== Closing All Positions ===")
        result = trade.close_all_positions()
        
        print(f"\nTotal positions found: {result['total']}")
        print(f"Successfully closed: {len(result['success'])}")
        print(f"Failed to close: {len(result['failed'])}")
        
        if result['success']:
            print("\n✅ Successfully closed positions:")
            for pos in result['success']:
                print(f"  - {pos['symbol']}: {pos['positionAmt']} (Order ID: {pos['orderId']})")
        
        if result['failed']:
            print("\n❌ Failed to close positions:")
            for pos in result['failed']:
                print(f"  - {pos['symbol']}: {pos['positionAmt']} (Error: {pos['error']})")
        
        return result
    except Exception as e:
        print(f"❌ Error closing all positions: {e}")
        return None

# Uncomment to test closing all positions
# close_all_positions()    