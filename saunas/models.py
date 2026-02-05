from django.db import models
from django.conf import settings


class SaunaDay(models.Model):
    area = models.ForeignKey(
        "accounts.Area",
        on_delete=models.CASCADE,
        related_name="sauna_days"
    )

    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("area", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.area.name} – {self.date}"


class SaunaSession(models.Model):
    sauna_day = models.ForeignKey(
        SaunaDay,
        on_delete=models.CASCADE,
        related_name="sessions"
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    sauna_name = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # dane operacyjne
    total_people = models.PositiveIntegerField(null=True, blank=True)
    women = models.PositiveIntegerField(null=True, blank=True)
    men = models.PositiveIntegerField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.sauna_name} {self.start_time}-{self.end_time}"
