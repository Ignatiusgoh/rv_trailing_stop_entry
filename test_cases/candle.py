import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import insertNewCandle
from dotenv import load_dotenv
load_dotenv()
import unittest, asyncio
import json

supabase_url = os.getenv("SUPABASE_URL")
supabase_api_key = os.getenv("SUPABASE_API_KEY")
supbase_jwt = os.getenv("SUPABASE_JWT")



class TestCandle(unittest.TestCase):

    def test_insert_mo(self, market_in_order_id):
        candle_data=json.dumps({
            "open": "139.10",
            "high": "149.10",
            "low": "129.10",
            "close": "138.10",
        })

        MO_order_id = market_in_order_id

        trade_metadata = json.dumps({
            'risk_amount': 10,
            'fee': 0.1,
            'portfolio_threshold': 20,
            'rv_period': 2,
            'ema_period': 9,
            'rv_threshold': 2.8,
            'trailing_percentage': 0.7
        })

        res = insertNewCandle(candle_data, MO_order_id, 0, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)
        print(res)

    def test_insert_sl(self):

        candle_data2=json.dumps({
            "open": "158.10",
            "high": "167.10",
            "low": "155.10",
            "close": "157.10",
        })
        SL_order_id = 2222

        trade_metadata = json.dumps({
            'risk_amount': 10,
            'fee': 0.1,
            'portfolio_threshold': 20,
            'rv_period': 2,
            'ema_period': 9,
            'rv_threshold': 2.8,
            'trailing_percentage': 0.7
        })

        res2 = insertNewCandle(candle_data2, SL_order_id, 0, trade_metadata, supabase_url, supabase_api_key, supbase_jwt)
        print(res2)

if __name__ == '__main__':
    asyncio.run(unittest.main())


