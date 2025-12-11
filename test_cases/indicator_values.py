import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.indicator_cache import CandleCache

from dotenv import load_dotenv

load_dotenv()

### TESTING LOG INTO SUPABASE ###


if __name__ == "__main__":
    cache = CandleCache()
    historical_data = cache.fetch_historical_data(symbol="SOLUSDT", interval="30m", limit=200)
    cache = CandleCache(historical_data=historical_data)

    rv = cache.calculate_relative_volume(period = 2)
    ema = cache.calculate_ema(period = 9)

    print(f"Open: {cache.candles[-1]['open']}")
    print(f"High: {cache.candles[-1]['high']}")
    print(f"Low: {cache.candles[-1]['low']}")
    print(f"Close: {cache.candles[-1]['close']}")
    print(f"Volume: {cache.candles[-1]['volume']}")
    print(f"Close Time: {cache.candles[-1]['close_time']}")
    print(f"RV: {rv}")
    print(f"EMA: {ema}")

