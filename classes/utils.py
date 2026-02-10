from datetime import time


def generate_hour_slots(start=6, end=22):
    """
    Generuje sloty godzinowe: 06:00–21:00
    """
    return [time(h, 0) for h in range(start, end)]


def build_hour_grid(events, hour_slots):
    """
    Grid: { "HH:MM": event or None }

    Jeden event na slot.
    Jeśli event zaczyna się w środku godziny (np 17:30),
    przypisujemy go do godziny startowej (17:00).
    """

    grid = {}

    # inicjalizacja pustego gridu
    for slot in hour_slots:
        key = slot.strftime("%H:%M")
        grid[key] = None

    # wrzucanie eventów
    for event in events:

        start_hour = event.start_time.hour
        key = f"{start_hour:02d}:00"

        if key in grid:
            grid[key] = event

    return grid
