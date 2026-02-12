from django.db import models
from django.conf import settings
from accounts.models import Area


class CashCount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
    )

    breakdown = models.JSONField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.area.code} — {self.total} zł"
