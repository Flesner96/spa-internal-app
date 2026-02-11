from datetime import time


def generate_hour_slots(start=6, end=22):
    """
    Generuje sloty godzinowe: 06:00–21:00
    """
    return [time(h, 0) for h in range(start, end)]


def build_hour_grid(events, hour_slots):
    """
    Grid: { "HH:MM": [event1, event2, ...] }
    """

    grid = {}

    # inicjalizacja pustych list
    for slot in hour_slots:
        key = slot.strftime("%H:%M")
        grid[key] = []

    # przypisanie eventów
    for event in events:
        key = f"{event.start_time.hour:02d}:00"

        if key in grid:
            grid[key].append(event)

    return grid

