from datetime import timedelta
from django.utils import timezone


def get_week_range(base_date=None):
    if base_date is None:
        base_date = timezone.localdate()

    start = base_date - timedelta(days=base_date.weekday())
    end = start + timedelta(days=6)

    return start, end
