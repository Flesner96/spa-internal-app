from datetime import timedelta, date
from django.utils import timezone


def get_week_range(base_date=None):
    if base_date is None:
        base_date = timezone.localdate()

    start = base_date - timedelta(days=base_date.weekday())
    end = start + timedelta(days=6)

    return start, end

def parse_polish_day_month(text: str):
    """
    '6.02' → date(2026, 2, 6)
    """
    if not text:
        return None

    try:
        day, month = text.split(".")
        today = timezone.localdate()

        return date(
            year=today.year,
            month=int(month),
            day=int(day),
        )
    except Exception:
        return None