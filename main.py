from utils.websocket_handler import candle_stream
from utils.logger import init_logger
from time import sleep
import utils.indicator_cache as indicator 
import utils.binancehelpers as binance
import utils.trade_executer as execute
import asyncio, logging, websockets
from utils.supabase_client import log_into_supabase, get_latest_group_id, get_latest_trades, insertNewCandle
import os
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
order_table_name = os.getenv("ORDER_TABLE")
supabase_api_key = os.getenv("SUPABASE_API_KEY")
supbase_jwt = os.getenv("SUPABASE_JWT")
# strategy = int(os.getenv("STRATEGY_ENV"))

symbol = "SOLUSDT"
interval = "30m"

risk_amount = 10
fee = 0.1
portfolio_threshold = 20
rv_period = 2
ema_period = 9
rv_threshold = 2.8
trailing_percentage = 0.7


# usdt_entry_size = risk_amount / ((sl_percentage + fee) / 100)
trade = execute.BinanceFuturesTrader()

async def main():
    init_logger()
    cache = indicator.CandleCache()
    historical_data = cache.fetch_historical_data(symbol=symbol, interval=interval, limit=200)
    cache = indicator.CandleCache(historical_data=historical_data)

    trade_metadata = json.dumps(dict(
        risk_amount=risk_amount,
        fee=fee,
        portfolio_threshold=portfolio_threshold,
        rv_period=rv_period,
        ema_period=ema_period,
        rv_threshold=rv_threshold,
        trailing_percentage=trailing_percentage,
    ))
    
    async for candle in candle_stream(symbol, interval):   # ← stays connected

        #### to discuss how to proceed with lei (we dont need this anymore because it is always going to be one trade at a time) ####
        group_id = get_latest_group_id(supabase_url=supabase_url, api_key=supabase_api_key, jwt=supbase_jwt)
        group_id += 1    
        #########################################################

        cache.add_candle(candle)

        rv = cache.calculate_relative_volume(period = rv_period)
        ema = cache.calculate_ema(period = ema_period)

        if rv is not None:
            logging.info(f"RV: {rv}")
        else:
            logging.info("RV: None")

        if ema is not None:
            logging.info(f"EMA: {ema}")
        else:
            logging.info("EMA: None")

        
        if binance.get_total_open_order() > 0:
            logging.info("There is an open order, not looking for entry")
            continue
        
        if cache.trading_window(cache.candles[-1]['timestamp']):
            logging.info("Trading window is open")
        else: 
            logging.info("Trading window is closed; only trading between 10pm to 6am SGT)")
            continue

        # if percentage_at_risk < portfolio_threshold: 
            # logging.info(f"Portfolio risk: {percentage_at_risk} percent lower than threshold: {portfolio_threshold}, looking for entry")
        
        last_close = cache.candles[-1]['close']
        last_open = cache.candles[-1]['open']
        last_high = cache.candles[-1]['high']
        last_low = cache.candles[-1]['low']

        candle_data = json.dumps(cache.candles[-1])
        

        strategy_condition_long = (
            (rv > rv_threshold and last_close > ema and last_open < ema)
        )
        strategy_condition_short = (
            (rv > rv_threshold and last_close < ema and last_open > ema)
        )

        if strategy_condition_long:                
            logging.info(f"Relative volume > {rv_threshold}, close price > {ema}, open price < {ema} ... Entering LONG")
            logging.info(f"Close price: {last_close}")
            logging.info(f"EMA: {ema}")
            logging.info(f"Open price: {last_open}")
            logging.info(f"Low price (stoploss price): {last_low}")
            
            stoploss_percentage = round((last_close - last_low)/last_close * 100, 2)
            usdt_entry_size = round(risk_amount / ((stoploss_percentage + fee) / 100), 2)
            sol_entry_size = round(usdt_entry_size / last_close, 2)
            logging.info(f"Stoploss percentage: {stoploss_percentage}%")
            logging.info(f"Entry size: {usdt_entry_size} USDT")
            logging.info(f"Entry size: {sol_entry_size} SOL")


            ###### ENTERING MARKET IN ORDER ######
            try:
                market_in = trade.place_market_order(symbol=symbol, side = "BUY", quantity=sol_entry_size)
                sleep(5)
                logging.info(market_in)
                market_in_order_id = market_in['orderId']

            except Exception as e:
                logging.error(f"Something went wrong executing MARKET IN ORDER, error: {e}")
                return e
            
            ### Inserting MO candle data in DB ###
            try:
                MO_order_id = market_in['orderId']
                insertNewCandle(candle_data, MO_order_id, group_id, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)

            except Exception as e:
                logging.error(f"Something went wrong inserting new candle, error: {e}")
                return e
        
            ###### ENTERING STOP LOSS ORDER ######
            try: 
                stoploss_order = trade.set_stop_loss(symbol=symbol, side="SELL", stop_price=last_low)
                sleep(5)
                logging.info(f"Stop loss order response: {stoploss_order}")
                # Algo Order API may return 'clientAlgoId' or 'orderId'
                stoploss_order_id = stoploss_order.get('algoId')
                if not stoploss_order_id:
                    logging.error(f"❌ Stop loss order response missing orderId/clientAlgoId: {stoploss_order}")
                    raise Exception(f"Stop loss order failed: {stoploss_order}")

            except Exception as e:
                logging.error(f"Something went wrong executing STOPLOSS ORDER, error: {e}")
                return e
            
            ### Inserting SL candle data in DB ###
            try:
                SL_order_id = market_in['orderId']
                
                insertNewCandle(candle_data, SL_order_id, group_id, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)

            except Exception as e:
                logging.error(f"Something went wrong inserting new candle, error: {e}")
                return e
            
        
        elif strategy_condition_short:
            logging.info(f"Relative volume > {rv_threshold}, close price < {ema}, open price > {ema} ... Entering SHORT")
            logging.info(f"Close price: {last_close}")
            logging.info(f"EMA: {ema}")
            logging.info(f"Open price: {last_open}")
            logging.info(f"High price (stoploss price): {last_high}")
            
            stoploss_percentage = round(((last_high - last_close)/last_close * 100), 2)
            usdt_entry_size = round(risk_amount / ((stoploss_percentage + fee) / 100),2)
            sol_entry_size = round(usdt_entry_size / last_close, 2)
            logging.info(f"Stoploss percentage: {stoploss_percentage}%")
            logging.info(f"Entry size: {usdt_entry_size}")
            logging.info(f"Entry size: {sol_entry_size} SOL")

            ###### ENTERING MARKET IN ORDER ######
            try:
                market_in = trade.place_market_order(symbol=symbol, side = "SELL", quantity=sol_entry_size)
                sleep(5)
                logging.info(market_in)
                market_in_order_id = market_in['orderId']

            except Exception as e:
                logging.error(f"Something went wrong executing MARKET IN ORDER, error: {e}")
                return e

            ### Inserting candle data in DB ###
            try:
                MO_order_id = market_in['orderId']
                insertNewCandle(candle_data, MO_order_id, group_id, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)

            except Exception as e:
                logging.error(f"Something went wrong inserting new candle, error: {e}")
                return e

            actual_entry_price = binance.entry_price(market_in_order_id)
            logging.info(f"Actual entry price: {actual_entry_price}")

            trailing_value = (last_high - actual_entry_price) * trailing_percentage
            logging.info(f"Trailing value: {trailing_value}")
            
            trailing_price = actual_entry_price - trailing_value
            logging.info(f"Stoploss will be shifted when price is at {trailing_price}")  

            next_stoploss_price = last_high - trailing_value   
            logging.info(f"Next stoploss price: {next_stoploss_price}")    
        
            ###### ENTERING STOP LOSS ORDER ######
            try: 
                stoploss_order = trade.set_stop_loss(symbol=symbol, side="BUY", stop_price=last_high)
                sleep(5)
                logging.info(f"Stop loss order response: {stoploss_order}")
                # Algo Order API may return 'clientAlgoId' or 'orderId'
                stoploss_order_id = stoploss_order.get('algoId')
                if not stoploss_order_id:
                    logging.error(f"❌ Stop loss order response missing orderId/clientAlgoId: {stoploss_order}")
                    raise Exception(f"Stop loss order failed: {stoploss_order}")

            except Exception as e:
                logging.error(f"Something went wrong executing STOPLOSS ORDER, error: {e}")
                return e

            ### Inserting SL candle data in DB ###
            try:
                SL_order_id = market_in['orderId']
                insertNewCandle(candle_data, SL_order_id, group_id, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)

            except Exception as e:
                logging.error(f"Something went wrong inserting new candle, error: {e}")
                return e

        else: 
            logging.info('No entry conditions met')
        
asyncio.run(main())