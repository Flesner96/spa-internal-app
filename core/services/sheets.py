import gspread
import json
import os

from google.oauth2.service_account import Credentials
from django.core.cache import cache


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CACHE_TTL = 600


SHEETS = {
    "RC": {
        "spreadsheet": "15xzRT871M5bqXOS3atuNh9U9MDbfyCbwmUAGv5MZRa0",
        "worksheet": "Display",
    },
    # przyszłość:
    # "SA": {
    #     "spreadsheet": "...",
    #     "worksheet": "Display",
    # },
    # "SP": {
    #     "spreadsheet": "...",
    #     "worksheet": "Display",
    # },
}


def fetch_schedule(area):

    config = SHEETS.get(area)

    if not config:
        return []

    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON missing")

    creds_dict = json.loads(creds_json)

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_key(
        config["spreadsheet"]
    ).worksheet(config["worksheet"])

    return sheet.get_all_values()


def get_schedule(area):

    cache_key = f"schedule_raw_{area}"

    data = cache.get(cache_key)

    if data:
        return data

    data = fetch_schedule(area)

    cache.set(cache_key, data, CACHE_TTL)

    return data