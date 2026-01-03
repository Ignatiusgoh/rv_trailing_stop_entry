import time
import hmac
import hashlib
import requests
import logging 
import os 
from dotenv import load_dotenv

load_dotenv()

class BinanceFuturesTrader:
    BASE_URL = 'https://fapi.binance.com'

    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.max_retries = 10
        self.retry_delays = 2

    def _sign(self, params):
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(self.api_secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        return signature

    def _post(self, endpoint, params):
        params['timestamp'] = int(time.time() * 1000)
        params['signature'] = self._sign(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.post(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            logging.error("HTTP Error: ", e)
            logging.error("Response body:", response.text)
        return response.json()

    def _get(self, endpoint, params=None):
        """Helper method for GET requests"""
        if params is None:
            params = {}
        params['timestamp'] = int(time.time() * 1000)
        params['signature'] = self._sign(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.get(f"{self.BASE_URL}{endpoint}", headers=headers, params=params)
        try:
            response.raise_for_status()
        except Exception as e:
            logging.error("HTTP Error: ", e)
            logging.error("Response body:", response.text)
        return response.json()

    def set_leverage(self, symbol, leverage):
        params = {'symbol': symbol, 'leverage': leverage}
        return self._post('/fapi/v1/leverage', params)

    def place_market_order(self, symbol, side, quantity):
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'MARKET',
            'quantity': quantity
        }
        for attempt in range(1, self.max_retries + 1):
            try: 
                self.res = self._post('/fapi/v1/order', params)
                if 'orderId' in self.res:
                    logging.info(f"Successfully executed MARKET IN ORDER with ID: {self.res['orderId']}")
                    return self.res 
                else:
                    logging.warning(f"MARKET IN order response missing orderId: {self.res}")
            except Exception as e:
                logging.error(f"[Attempt {attempt}] Failed to MARKET IN | Error: {e}")
                if attempt == self.max_retries:
                    logging.critical("Max retries reached. Giving up.")
                    raise
                time.sleep(self.retry_delay)

    def set_stop_loss(self, symbol, side, stop_price):
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'STOP_MARKET',
            'stopPrice': stop_price,
            'closePosition': 'true'
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                self.res = self._post('/fapi/v1/order', params)
                if 'orderId' in self.res:
                    logging.info(f"Successfully executed STOPLOSS ORDER with ID: {self.res['orderId']}")
                else:
                    logging.warning(f"STOPLOSS order response missing orderId: {self.res}")
                return self.res
            except Exception as e:
                logging.error(f"[Attempt {attempt}] Failed to set stop loss | Error: {e}")
                if attempt == self.max_retries:
                    logging.critical("Max retries reached. Giving up.")
                    raise
                time.sleep(self.retry_delay)

    def set_take_profit_limit(self, symbol, side, stop_price, price, quantity): 
        # stop_price is when the order is triggered, price is the limit price 
        # for faster execution, set price < stop_price so that when the market price hit the stop_price, the order will be filled at limit price 
        # if price > stop_price then there is a chance the order gets stuck due to price pull back
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'TAKE_PROFIT',
            'stopPrice': stop_price,
            'price': price,
            'quantity': quantity,
            'timeInForce': 'GTC'
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                self.res = self._post('/fapi/v1/order', params)
                if 'orderId' in self.res:
                    logging.info(f"Successfully executed TAKEPROFIT ORDER with ID: {self.res['orderId']}")
                else:
                    logging.warning(f"TAKEPROFIT order response missing orderId: {self.res}")
                return self.res
            except Exception as e:
                logging.error(f"[Attempt {attempt}] Failed to set TAKEPROFIT | Error: {e}")
                if attempt == self.max_retries:
                    logging.critical("Max retries reached. Giving up.")
                    raise
                time.sleep(self.retry_delay)

    def get_open_positions(self):
        """
        Get all open positions (non-zero position amounts).
        
        Returns:
            list: List of positions with non-zero positionAmt
        """
        try:
            positions = self._get('/fapi/v2/positionRisk')
            open_positions = [
                pos for pos in positions 
                if float(pos.get('positionAmt', 0)) != 0.0
            ]
            return open_positions
        except Exception as e:
            logging.error(f"Error fetching open positions: {e}")
            return []

    def close_all_positions(self):
        """
        Close all open positions by placing market orders in the opposite direction.
        
        Returns:
            dict: Summary of closed positions with success/failure status
        """
        results = {
            'success': [],
            'failed': [],
            'total': 0
        }
        
        try:
            # Get all open positions
            open_positions = self.get_open_positions()
            results['total'] = len(open_positions)
            
            if not open_positions:
                logging.info("No open positions to close.")
                return results
            
            logging.info(f"Found {len(open_positions)} open position(s) to close.")
            
            # Close each position
            for position in open_positions:
                symbol = position['symbol']
                position_amt = float(position['positionAmt'])
                
                # Determine side: if positionAmt is positive, we need to SELL to close
                # If positionAmt is negative, we need to BUY to close
                side = "SELL" if position_amt > 0 else "BUY"
                quantity = abs(position_amt)
                
                try:
                    # Use closePosition parameter for safer closing
                    params = {
                        'symbol': symbol,
                        'side': side,
                        'type': 'MARKET',
                        'reduceOnly': 'true',  # Only reduce position, don't open new one
                        'quantity': quantity
                    }
                    
                    for attempt in range(1, self.max_retries + 1):
                        try:
                            response = self._post('/fapi/v1/order', params)
                            if 'orderId' in response:
                                logging.info(f"✅ Successfully closed {symbol} position: {position_amt} (Order ID: {response['orderId']})")
                                results['success'].append({
                                    'symbol': symbol,
                                    'positionAmt': position_amt,
                                    'orderId': response['orderId']
                                })
                                break
                            else:
                                logging.warning(f"⚠️ Close order response missing orderId for {symbol}: {response}")
                        except Exception as e:
                            logging.error(f"[Attempt {attempt}] Failed to close {symbol} position: {e}")
                            if attempt == self.max_retries:
                                results['failed'].append({
                                    'symbol': symbol,
                                    'positionAmt': position_amt,
                                    'error': str(e)
                                })
                                break
                            time.sleep(self.retry_delay)
                    
                    # Small delay between orders to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logging.error(f"Error closing position for {symbol}: {e}")
                    results['failed'].append({
                        'symbol': symbol,
                        'positionAmt': position_amt,
                        'error': str(e)
                    })
            
            logging.info(f"✅ Closed {len(results['success'])}/{results['total']} position(s) successfully.")
            if results['failed']:
                logging.warning(f"❌ Failed to close {len(results['failed'])} position(s).")
            
            return results
            
        except Exception as e:
            logging.error(f"❌ Error in close_all_positions: {e}")
            return results
                

