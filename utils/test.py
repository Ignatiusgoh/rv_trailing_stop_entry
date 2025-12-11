from supabase_client import log_into_supabase
import os 
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
api_key = os.getenv("SUPABASE_API_KEY")
jwt = os.getenv("SUPABASE_JWT")

data = {
    "group_id": 1,
    "order_id": 1,
    "type": "MO",
    "direction": "LONG",
    "current_stop_loss": 100,
    "trailing_value": 10,
    "trailing_price": 110,
    "next_stoploss_price": 120
}
log_into_supabase(data, supabase_url=supabase_url, api_key=api_key, jwt=jwt)