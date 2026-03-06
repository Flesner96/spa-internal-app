import gspread
import json
import os

from google.oauth2.service_account import Credentials
from django.core.cache import cache

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CACHE_KEY = "schedule_raw"
CACHE_TTL = 600


def fetch_schedule():

    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        "15xzRT871M5bqXOS3atuNh9U9MDbfyCbwmUAGv5MZRa0"
    ).worksheet("Display")

    return sheet.get_all_values()


def get_schedule():

    data = cache.get(CACHE_KEY)

    if data:
        return data

    data = fetch_schedule()

    cache.set(CACHE_KEY, data, CACHE_TTL)

    return data