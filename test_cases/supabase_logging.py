import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import log_into_supabase
import os 
from dotenv import load_dotenv

load_dotenv()

### TESTING LOG INTO SUPABASE ###

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
def test_log_into_supabase():
    try:
        response = log_into_supabase(data, supabase_url=supabase_url, api_key=api_key, jwt=jwt)
        if response.status_code == 200:
            print("Test passed")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_log_into_supabase()