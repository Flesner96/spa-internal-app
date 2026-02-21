from django.db import models


class PoolEvent(models.Model):

    EVENT_TYPES = [
        ("CL", "Zajęcia"),
        ("SW", "Nauka pływania"),
    ]

    event_type = models.CharField(max_length=2, choices=EVENT_TYPES)
    DAY_CHOICES = [
    (0, "Poniedziałek"),
    (1, "Wtorek"),
    (2, "Środa"),
    (3, "Czwartek"),
    (4, "Piątek"),
    (5, "Sobota"),
    (6, "Niedziela"),
]

    day_of_week = models.IntegerField(choices=DAY_CHOICES)

    name = models.CharField(max_length=120)
    instructor = models.CharField(max_length=120, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()

    lane_start = models.IntegerField(default=1)
    lane_end = models.IntegerField(default=1)
