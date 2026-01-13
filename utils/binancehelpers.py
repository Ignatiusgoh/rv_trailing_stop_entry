from binance.client import Client
import logging
import requests
import time
import os 
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

client = Client(api_key, api_secret)

def get_usdt_balance():
    while True:
        try:
            futures_account = client.futures_account()  # USDT-margined futures
            assets = futures_account['assets']
            for asset in assets:
                if asset['asset'] == 'USDT':
                    marginBalance = asset['marginBalance']

            return float(marginBalance)

        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching positions: {e}. Retrying")
            time.sleep(0.1)

def percentage_at_risk(risk_amount):
    while True:
        try:
            positions = client.futures_account()['positions']

            open_positions = [
                pos for pos in positions
                if float(pos['positionAmt']) != 0.0
            ]
            if len(open_positions) != 0:
                amount_at_risk = risk_amount*len(open_positions)
                percentage_at_risk = round((amount_at_risk / get_usdt_balance() * 100) ,2)
            else:
                print("No open positions")
                percentage_at_risk = 0

            return percentage_at_risk

        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching positions: {e}. Retrying")
            time.sleep(0.1)

def entry_price(order_id):
    while True:
        try:
            trades = client.futures_account_trades(symbol="SOLUSDT")
            print(trades)
            matching_trades = [t for t in trades if t['orderId'] == order_id]

            if not matching_trades:
                print("❌ No trades found for that order ID.")
            else:
                total_qty = sum(float(t['qty']) for t in matching_trades)
                weighted_sum = sum(float(t['price']) * float(t['qty']) for t in matching_trades)
                avg_entry_price = weighted_sum / total_qty

            return avg_entry_price

        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching positions: {e}. Retrying")
            time.sleep(0.1)

def get_total_open_order():
    while True: 
        try: 
            open_orders = client.futures_get_open_orders()
            return len(open_orders)
        except Exception as e: 
            logging.warning(f"⚠️ Error fetching open orders: {e}. Retrying")
            time.sleep(0.1)

def get_max_leverage(symbol="SOLUSDT"):
    """
    Get the maximum leverage available for a symbol.
    
    Args:
        symbol (str): Trading pair symbol (default: "SOLUSDT")
    
    Returns:
        int: Maximum leverage available for the symbol, or None if error
    """
    while True:
        try:
            # Get leverage brackets for the symbol
            leverage_brackets = client.futures_leverage_bracket(symbol=symbol)
            
            if not leverage_brackets or len(leverage_brackets) == 0:
                logging.warning(f"⚠️ No leverage brackets found for {symbol}")
                return None
            
            # The leverage_brackets is a list, get the first element
            bracket_data = leverage_brackets[0]
            
            # The brackets array contains leverage tiers, find the maximum initialLeverage
            if 'brackets' in bracket_data and bracket_data['brackets']:
                max_leverage = max(
                    tier.get('initialLeverage', 0) 
                    for tier in bracket_data['brackets']
                )
                return max_leverage if max_leverage > 0 else None
            else:
                logging.warning(f"⚠️ No brackets found in leverage data for {symbol}")
                return None
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"⚠️ Error fetching leverage for {symbol}: {e}. Retrying")
            time.sleep(0.1)
        except Exception as e:
            logging.error(f"❌ Unexpected error fetching leverage for {symbol}: {e}")
            return None


if __name__ == '__main__':
    print(get_usdt_balance())
    print(f"Max leverage for SOLUSDT: {get_max_leverage('SOLUSDT')}")