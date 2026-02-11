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


def build_lane_conflict_grid(events, hour_slots):
    """
    grid[godzina][tor] = lista eventów
    """

    LANES = 4

    grid = {}

    for slot in hour_slots:
        key = slot.strftime("%H:%M")
        grid[key] = [[] for _ in range(LANES)]

    for event in events:

        start = event.start_time.hour
        end = event.end_time.hour

        for hour in range(start, end):

            key = f"{hour:02d}:00"

            if key not in grid:
                continue

            for lane in range(
                event.lane_start - 1,
                event.lane_end
            ):
                grid[key][lane].append(event)

    return grid
