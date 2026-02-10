from django.db import models


class PoolEvent(models.Model):

    EVENT_TYPES = [
        ("CL", "Zajęcia"),
        ("SW", "Nauka pływania"),
    ]

    event_type = models.CharField(max_length=2, choices=EVENT_TYPES)

    day_of_week = models.IntegerField()  # 0–6

    name = models.CharField(max_length=120)
    instructor = models.CharField(max_length=120, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    lane_start = models.IntegerField(default=1)
    lane_end = models.IntegerField(default=1)
