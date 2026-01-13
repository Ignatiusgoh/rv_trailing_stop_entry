import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   
from utils.supabase_client import log_into_supabase
import utils.binancehelpers as binance
from dotenv import load_dotenv
import time

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
order_table_name = os.getenv("ORDER_TABLE")
supabase_api_key = os.getenv("SUPABASE_API_KEY")
supbase_jwt = os.getenv("SUPABASE_JWT")

### TESTING PLACING MARKET ORDER ###

trade = BinanceFuturesTrader()

try: 
    set_leverage = trade.set_leverage(symbol="SOLUSDT", leverage=30)
    print(set_leverage)
except Exception as e:
    print(f"Error: {e}")
try:
    response = trade.place_market_order(symbol="SOLUSDT", side="BUY", quantity=3)
    market_in_order_id = response['orderId']
    time.sleep(3)
    actual_entry_price = binance.entry_price(market_in_order_id)
    print(response)
    data = {
        "group_id": 0,
        "order_id": market_in_order_id,
        "type": "MO",
        "direction": "LONG",
        "current_stop_loss": 100,
        "trailing_value": 120,
        "trailing_price": 120,
        "next_stoploss_price": 120
    }
    try:
        log_into_supabase(data, supabase_url=supabase_url, api_key=supabase_api_key, jwt=supbase_jwt)
        print("MARKET IN Trade logged to Supabase")
    
    except Exception as e:
        print(f"Failed to log MARKET IN trade to Supabase: {e}")

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