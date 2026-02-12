from decimal import Decimal
from .constants import DENOMINATIONS


def calculate_total(breakdown: dict) -> Decimal:
    total = Decimal("0")

    for key, qty in breakdown.items():
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            qty = 0

        total += DENOMINATIONS[key] * qty

    return total
