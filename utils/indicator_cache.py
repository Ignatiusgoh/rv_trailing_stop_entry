import numpy as np
from collections import deque
import requests, time 

class CandleCache:
    def __init__(self, max_candles: int = 200, volume_period: int = 12, historical_data: list = None):
        self.candles = deque(maxlen=max_candles)
        self.volume_period = volume_period

        
        # If historical data is passed, add it to the candles deque
        if historical_data:
            for candle in historical_data:
                if candle['close_time'] < int(time.time() * 1000):
                    self.add_candle(candle)

    def fetch_historical_data(self, symbol: str, interval: str, limit: int = 100):
        """ Fetch historical candlestick data from an API (e.g., Binance). """
        # Example for Binance API, you can replace with any API you're using
        url = f"https://fapi.binance.com/fapi/v1/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Format the data to match the candle format
            formatted_data = [{
                'timestamp': candle[0],
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5]),
                'close_time': candle[6],
                'quote_asset_volume': float(candle[7]),
                'number_of_trades': int(candle[8]),
                'taker_buy_base_asset_volume': float(candle[9]),
                'taker_buy_quote_asset_volume': float(candle[10]),
            } for candle in data]

            return formatted_data
        else:
            return None

    def add_candle(self, candle: dict):
        """ Add a new candle to the cache. """
        self.candles.append(candle)

    def get_last_n_closes(self, n: int):
        """ Retrieve the close prices of the last N candles. """
        if len(self.candles) < n:
            return None
        return [c['close'] for c in list(self.candles)[-n:]]

    def get_last_n_volumes(self, n: int):
        """ Retrieve the volume of the last N candles. """
        if len(self.candles) < n:
            return None
        return [c['volume'] for c in list(self.candles)[-n:]]


    def calculate_relative_volume(self,period: int = 2):
        """ Calculate the Relative Volume (RV) based on the last 'period' candles. """
        volumes = self.get_last_n_volumes(period)
        if volumes is None:
            return None # Not enough data yet
            
        current_volume = volumes[-1]
        previous_volumes = volumes[:-1]
        avg_previous_volume = np.mean(previous_volumes)

        rv = current_volume / avg_previous_volume
        return rv

    def calculate_ema(self, period: int = 9):
        """ Calculate the Exponential Moving Average (EMA) using pandas ewm(span=period) method. """
        # Get enough closes to calculate EMA properly (need at least period candles)
        closes = self.get_last_n_closes(50)
        if closes is None or len(closes) < period:
            return None  # Not enough data yet

        # Convert to numpy array for easier manipulation
        closes_array = np.array(closes)
        
        # Calculate alpha for pandas ewm(span=period) method
        # alpha = 2 / (span + 1)
        alpha = 2.0 / (period + 1.0)
        
        # Initialize EMA with first value
        ema = closes_array[0]
        
        # Calculate EMA iteratively for remaining values
        for i in range(1, len(closes_array)):
            ema = alpha * closes_array[i] + (1 - alpha) * ema
        
        return ema






    # def calculate_bollinger_bands(self, period: int = 20, num_std_dev: float = 2.0):
    #     """ Calculate Bollinger Bands (SMA + upper/lower bands). """
    #     closes = self.get_last_n_closes(period)
    #     if closes is None:
    #         return None  # Not enough data yet

    #     arr = np.array(closes)
    #     sma = np.mean(arr)
    #     std = np.std(arr)

    #     upper_band = sma + num_std_dev * std
    #     lower_band = sma - num_std_dev * std

    #     return {
    #         "sma": sma,
    #         "upper": upper_band,
    #         "lower": lower_band
    #     }


    # def calculate_rsi(self, period: int = 14):
    #     """Calculate the Relative Strength Index (RSI) using Wilder's smoothing method."""
    #     closes = self.get_last_n_closes(period + 100)  # Get more data for smoothing
    #     if closes is None or len(closes) < period + 1:
    #         return None  # Not enough data

    #     deltas = np.diff(closes)
    #     gains = np.where(deltas > 0, deltas, 0)
    #     losses = np.where(deltas < 0, -deltas, 0)

    #     # First average gain/loss
    #     avg_gain = np.mean(gains[:period])
    #     avg_loss = np.mean(losses[:period])

    #     for i in range(period, len(gains)):
    #         gain = gains[i]
    #         loss = losses[i]
    #         avg_gain = (avg_gain * (period - 1) + gain) / period
    #         avg_loss = (avg_loss * (period - 1) + loss) / period

    #     if avg_loss == 0:
    #         return 100

    #     rs = avg_gain / avg_loss
    #     rsi = 100 - (100 / (1 + rs))

    #     self.rsi_values.append(rsi)  # Store the latest RSI value
    #     return rsi
    
    # def get_previous_rsi(self):
    #     """Get the previous RSI value without recalculating"""
    #     if len(self.rsi_values) >= 2:
    #         return list(self.rsi_values)[-2]  # Return second-to-last RSI value
    #     return None
    
    # def get_current_rsi(self):
    #     """Get the most recent RSI value"""
    #     if len(self.rsi_values) > 0:
    #         return self.rsi_values[-1]
    #     return None

    ##### This relative volume accounts for the current volume in its calculation
    # def calculate_relative_volume(self):
    #     """ Calculate the Relative Volume (RV) based on the last 'volume_period' candles. """
    #     volumes = self.get_last_n_volumes(self.volume_period)
    #     if volumes is None or len(volumes) < self.volume_period:
    #         return None  # Not enough data yet

    #     print("candles used: ", volumes)
    #     print("current volume: ", volumes[-1])
    #     avg_volume = np.mean(volumes)  # Average volume of the last N candles
    #     current_volume = volumes[-1]  # Volume of the most recent candle

    #     rv = current_volume / avg_volume
    #     return rv


