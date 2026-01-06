import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache
from utils.trade_executer import BinanceFuturesTrader   
from utils.supabase_client import log_into_supabase
from dotenv import load_dotenv


trade = BinanceFuturesTrader()

try:
    close_all_positions = trade.close_all_positions()
    print(close_all_positions)
except Exception as e:
    print(f"Error: {e}")