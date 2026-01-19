from supabase import create_client, Client
from supabase.client import ClientOptions
import httpx
import os
from dotenv import load_dotenv
load_dotenv()
def get_supabase_client():
    httpx_client = httpx.Client(
        timeout=httpx.Timeout(
            connect=5.0,
            read=10.0,
            write=10.0,
            pool=5.0,
        ),
        verify=True,  # or False if you really need it
    )

    options = ClientOptions(
        httpx_client=httpx_client
    )

    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY"),
        options=options,
    )