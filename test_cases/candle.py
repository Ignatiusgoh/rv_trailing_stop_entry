import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import insertNewCandle
from dotenv import load_dotenv
load_dotenv()
import unittest, asyncio
import json

supabase_url = os.getenv("SUPABASE_URL")
supabase_api_key = os.getenv("SUPABASE_API_KEY")
supbase_jwt = os.getenv("SUPABASE_JWT")



class TestCandle(unittest.TestCase):

    def test_insert(self):
        candle_data=json.dumps({
            "open": "139.10",
            "high": "149.10",
            "low": "129.10",
            "close": "138.10",
        })
        candle_data2=json.dumps({
            "open": "158.10",
            "high": "167.10",
            "low": "155.10",
            "close": "157.10",
        })
        MO_order_id = 1111
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

        res = insertNewCandle(candle_data, MO_order_id, trade_metadata)
        res2 = insertNewCandle(candle_data2, SL_order_id, trade_metadata)
        print(res)
        print(res2)


if __name__ == '__main__':
    asyncio.run(unittest.main())


