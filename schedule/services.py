from django.core.cache import cache
from core.services.sheets import fetch_sheet


CACHE_TTL = 600


SHEETS = {
    "RC": {
        "spreadsheet": "15xzRT871M5bqXOS3atuNh9U9MDbfyCbwmUAGv5MZRa0",
        "worksheet": "Display",
    },
}


def fetch_schedule(area):

    config = SHEETS.get(area)

    if not config:
        return []

    return fetch_sheet(
        config["spreadsheet"],
        config["worksheet"]
    )


def get_schedule(area):

    cache_key = f"schedule_raw_{area}"

    data = cache.get(cache_key)

    if data:
        return data

    data = fetch_schedule(area)

    cache.set(cache_key, data, CACHE_TTL)

    return data