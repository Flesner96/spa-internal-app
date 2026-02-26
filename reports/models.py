from django.db import models
from django.conf import settings
from accounts.models import Area

class ShiftCloseReport(models.Model):

    class ShiftType(models.TextChoices):
        MORNING = "morning", "Poranna"
        AFTERNOON = "afternoon", "Popołudniowa"

    area = models.ForeignKey(Area, on_delete=models.PROTECT)

    shift_date = models.DateField()
    shift_type = models.CharField(
        max_length=12,
        choices=ShiftType.choices
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    created_at = models.DateTimeField(auto_now_add=True)


    closing_cash = models.DecimalField(max_digits=10, decimal_places=2)

    cash_removed = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    auto_prefilled = models.BooleanField(default=False)

    laundry_delivery = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-shift_date", "-shift_type", "-created_at"]


class ShiftHandoverNote(models.Model):
    area = models.OneToOneField(Area, on_delete=models.CASCADE)
    content = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )