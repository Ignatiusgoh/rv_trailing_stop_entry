import sys
import os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import log_into_supabase
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
    "current_stop_loss": 95,
    "trailing_value": 5,
    "trailing_price": 105,
    "next_stoploss_price": 105
}

sldata = {
    "group_id": 1,
    "order_id": 2,
    "type": "SL",
    "direction": "LONG",
    "current_stop_loss": 95,
    "trailing_value": 5,
    "trailing_price": 105,
    "next_stoploss_price": 105
}

def test_log_into_supabase():
    try:
        response = log_into_supabase(data, supabase_url=supabase_url, api_key=api_key, jwt=jwt)
        # On success, log_into_supabase returns a list (from response.json())
        # On error, it returns a dict with 'error' and 'status_code' keys
        if isinstance(response, list) and len(response) > 0:
            print("✅ Test passed - MO Data successfully logged to Supabase")
            print(f"Response: {response}")
        elif isinstance(response, dict) and 'error' in response:
            print(f"❌ Test failed - Error: {response.get('error')}")
            print(f"Status code: {response.get('status_code')}")
        else:
            print(f"⚠️ Unexpected response format: {response}")
        
        responsesl = log_into_supabase(sldata, supabase_url=supabase_url, api_key=api_key, jwt=jwt)
        # On success, log_into_supabase returns a list (from response.json())
        # On error, it returns a dict with 'error' and 'status_code' keys
        if isinstance(response, list) and len(response) > 0:
            print("✅ Test passed - SL Data successfully logged to Supabase")
            print(f"Response: {response}")
        elif isinstance(response, dict) and 'error' in response:
            print(f"❌ Test failed - Error: {response.get('error')}")
            print(f"Status code: {response.get('status_code')}")
        else:
            print(f"⚠️ Unexpected response format: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_log_into_supabase()