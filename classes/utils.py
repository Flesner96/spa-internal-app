from datetime import time


def generate_hour_slots(start=6, end=22):
    """
    Generuje sloty godzinowe: 06:00–21:00
    """
    return [time(h, 0) for h in range(start, end)]


def build_hour_grid(events, hour_slots):
    """
    Grid:
    {
        "16:00": [event1, event2],
        "17:00": [],
    }
    """

    grid = {}

    # inicjalizacja
    for slot in hour_slots:
        key = slot.strftime("%H:%M")
        grid[key] = []

    # przypisanie eventów
    for event in events:
        start_hour = event.start_time.hour
        end_hour = event.end_time.hour

        for hour in range(start_hour, end_hour):
            key = f"{hour:02d}:00"

            if key in grid:
                grid[key].append(event)

    return grid




def build_combined_grid(events, hour_slots):
    """
    Grid dla widoku combined:
    {
        "HH:MM": [
            {"events": [...], "conflict": bool},
            ...
        ]
    }
    """

    grid = {}

    for slot in hour_slots:
        key = slot.strftime("%H:%M")
        grid[key] = [
            {"events": [], "conflict": False}
            for _ in range(4)
        ]

    for event in events:
        key = f"{event.start_time.hour:02d}:00"

        if key not in grid:
            continue

        for lane in range(event.lane_start - 1, event.lane_end):
            grid[key][lane]["events"].append(event)

    # konflikt detection
    for key in grid:
        for lane in grid[key]:
            if len(lane["events"]) > 1:
                lane["conflict"] = True

    return grid
