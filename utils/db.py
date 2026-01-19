import os
from dotenv import load_dotenv
from utils.db_connection import get_connection
from utils.supabase_client_lei import get_supabase_client
import logging
from typing import Optional



from datetime import datetime

load_dotenv()
supabase = get_supabase_client()
env = os.getenv("ENV")
orders_table = "orders" if env=="prod" else "test_orders"
order_groups_table = "order_groups" if env=="prod" else "test_order_groups"
trades_table = "trades" if env=="prod" else "test_trades"
candles_table = "candles" if env=="prod" else "test_candles"

def get_one_order(order_id):
    """Gets one order"""
    try:
        res = (
            supabase.table(orders_table)
            .select("*")
            .eq("order_id", order_id)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)

def get_orders():
    """Get all orders"""
    try:
        res = (
            supabase.table(orders_table)
            .select("*")
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)

def delete_orders():
    """Delete all orders"""
    try:
        res = (
            supabase.table(order_groups_table)
            .delete()
            .neq("order_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def delete_order_groups():
    """Delete all order groups"""
    try:
        res = (
            supabase.table(orders_table)
            .delete()
            .neq("order_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def delete_trades():
    """Delete all trades table"""
    try:
        res = (
            supabase.table(trades_table)
            .delete()
            .neq("group_id", 0)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)
        
def insertNewOrderByType(order_type, order_data):
    logging.info(f"✏️ Attempting to insert new order into DB... Order Type: {order_type}")
    logging.info(f"Order Data: {order_data}")
    try:
        newOrder = {
            "order_id":order_data["order_id"],
            "status":order_data["status"],
            "direction":order_data["direction"],
            "symbol":order_data["symbol"],
            "order_type":order_data["type"],
            "ask_price":None if order_data["type"] == "MARKET" else order_data["ask_price"], # Ask Price is none,
            "filled_price":None, # Filled Price Price is none
            "side":order_data["side"],
            "qty": order_data['qty'],
            "created_at": str(datetime.fromtimestamp(order_data["created_at"]/1000)),
            "updated_at": None,
        }
        res = (
            supabase.table(orders_table)
            .insert(newOrder)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

        
def findByIdAndUpdateFilledMarketOrder(order_id, order_data):
    logging.info(f"✏️ Attempting to UPDATE order {order_id} to FILLED")
    try:
        updated_market_order = {
            "status":order_data["status"],
            "ask_price":order_data['ask_price'],
            "filled_price":order_data['filled_price'],
            "updated_at": str(datetime.fromtimestamp(order_data["updated_at"]/1000)),
        }
        res = (
            supabase.table(orders_table)
            .update(updated_market_order)
            .eq("order_id", order_id)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def findByIdAndUpdateFilledSLOrder(order_id, order_data):
    logging.info(f"✏️ Attempting to UPDATE order {order_id} to FILLED")
    try:
        updated_sl_order = {
            "status":order_data["status"],
            "filled_price":order_data['filled_price'],
            "updated_at": str(datetime.fromtimestamp(order_data["updated_at"]/1000)),
        }
        res = (
            supabase.table(orders_table)
            .update(updated_sl_order)
            .eq("order_id", order_id)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)


def findByIdAndCancel(order_id, order_data):
    '''
    Updates the status of the order to be cancelled
    '''
    print(f"✏️ Attempting to UPDATE order {order_id} to CANCELED")
    try:
        res = (
            supabase.table(orders_table)
            .update({"status": order_data['status'], "updated_at": str(datetime.fromtimestamp(order_data["updated_at"]/1000))})
            .eq("order_id", order_id)
            .execute()
        )
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def insertNewTrade(group_id, order_data):
    logging.info(f"✏️ Attempting to insert new trade into DB with group_id: {group_id}, order_data: {order_data}")
    try:
        newTrade = {
            "group_id": group_id,
            "symbol": order_data["symbol"],
            "direction":order_data["direction"],
            "entry_time": str(datetime.fromtimestamp(order_data["updated_at"]/1000)),
            "exit_time": None, # This is entered only upon exit
            "entry_price":order_data["filled_price"], 
            "exit_price":None, # This is entered only upon exit
            "qty": order_data["qty"],
            "realized_pnl": None,# This is entered only upon exit
            "is_closed": False,
            "fees": None # This is entered only upon exit
        }
        logging.info(f"New trade object: {newTrade}")
        res = (
            supabase.table(trades_table)
            .insert(newTrade)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully inserted new trade with group_id {group_id} into trades table.")
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)

def get_entry_price_for_trade(group_id):
    try:
        res = (
            supabase.table(trades_table)
            .select("*")
            .eq("group_id", group_id)
            .execute()
        )
        if not res.data:
            return None
        return res.data[0]['entry_price']
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)

def updateTrade(group_id, order_data):
    logging.info(f"✏️ Attempting to update trade with group_id {group_id}...")
    direction = order_data['direction']
    try:
        market_fee = 0.0005
        limit_fee = 0.0002
        entry_price = float(get_entry_price_for_trade(group_id))
        exit_price = float(order_data['filled_price'])
        order_type = order_data['type'] # # MARKET / TAKE_PROFIT / STOP_MARKET
        qty = float(order_data['qty'])
        fee = (entry_price * qty * market_fee) + (exit_price * qty * market_fee)
        realized_pnl_without_fee = (exit_price - entry_price) * qty if direction == 'LONG' else -(exit_price - entry_price) * qty
        realized_pnl = round(realized_pnl_without_fee - fee, 3)

        updated_trade = {
            "exit_time":str(datetime.fromtimestamp(order_data["updated_at"]/1000)),
            "exit_price":order_data['filled_price'],
            "realized_pnl":realized_pnl,
            "is_closed": True,
            "fees": fee
        }
        res = (
            supabase.table(trades_table)
            .update(updated_trade)
            .eq("group_id", group_id)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully updated trade with group_id {group_id} in the trades table.")
        return res
    except Exception as e: 
        print("There's an issue updating supabase table: ", e)


def get_latest_group_id() -> Optional[int]:
    logging.info("✏️ Trying to get the latest group_id")
    try:
        res = (
            supabase.table(order_groups_table)
            .select("group_id", count="exact")
            .order("group_id", desc=True)
            .limit(1)
            .execute()
        )
        logging.info(f"Retrieved {res} from db")
        if not res.data:
            logging.info("No latest groupId found from group_orders table")
            return None
        return res.data[0]['group_id']
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)
    

def get_group_id_by_order(order_id) -> Optional[int]:
    logging.info(f"✏️ Trying to get latest group_id by order: {order_id}")
    try:
        res = (
            supabase.table(order_groups_table)
            .select("*")
            .eq("order_id", order_id)
            .execute()
        )
        logging.info(f"All order_groups found from DB:", res)
        if not res.data:
            logging.info(f"No associated group_id found for order_id: {order_id}")
            return None
        logging.info(f'Returning {res.data[0]['group_id']} from get_group_id_by_order function')
        return res.data[0]['group_id']
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)

def insertNewOrderGroup(new_group_id, order_data) -> Optional[int]:
    group_data = {
                    "group_id": new_group_id,
                    "order_id": order_data['order_id'],
                    "type": "MO",
                    "direction": order_data['direction'],
                    "current_stop_loss": None,
                    "trailing_value": None,
                    "trailing_price": None,
                    "next_stoploss_price": None,
                    "created_at": str(datetime.fromtimestamp(order_data["updated_at"]/1000))
                    }
    logging.info(f"✏️ Trying to insert a new order_group record with params: {group_data}")
    try:
        res = (
            supabase.table(order_groups_table)
            .insert(group_data)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully inserted new entry with group_id {new_group_id} into order_group table.")
        return res
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)

def find_remaining_order(group_id, remaining_order):
    logging.info(f"✏️ Trying to get remaining order_id of type {remaining_order} by group_id: {group_id}")
    
    try:
        res = (
            supabase.table(order_groups_table)
            .select("*")
            .eq("group_id", group_id)
            .eq("type", remaining_order)
            .execute()
        )
        if not res.data:
            logging.info(f"Can't find record")
            return None
        return res.data[0]['order_id']
    except Exception as e: 
        print("There's an issue getting one order from supabase: ", e)

def does_BE_exist_for_order_group(group_id) -> bool:
    logging.info(f"✏️ Trying to see if BE exists for group_id: {group_id}")
    try:
        res = (
            supabase.table(order_groups_table)
            .select("*")
            .eq("group_id", group_id)
            .eq("type", "BE")
            .execute()
        )
        if not res.data: # len 0 array -> this could also happen if group_id doesn't contain any trades !! potential source of bug
            logging.info(f"BE doesn't exist for res: {res}")
            return False
        else:
            logging.info(f"BE exists for res: {res}")
            return True
    except Exception as e: 
        logging.error(f"There's an issue getting one order from supabase: {e}")

def insertNewCandle(candle_data, order_id, trade_metadata,) -> Optional[int]:
    logging.info(f"OrderID: {order_id} | Inserting candle data into candles table: {candle_data}")
    logging.info(f"Trade Metadata: {trade_metadata}")

    candle_data = {
        "order_id": order_id,
        "candle_data": candle_data,
        "trade_metadata": trade_metadata
    }
    
    try:
        res = (
            supabase.table(candles_table)
            .insert(candle_data)
            .execute()
        )
        if res.data:
            logging.info(f"Successfully inserted new entry with order_id {order_id} into order_group table.")
        return res
    except Exception as e: 
        print("There's an issue getting supabase table: ", e)