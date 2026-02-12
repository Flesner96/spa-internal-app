from django import forms
from .models import PoolEvent


class PoolEventForm(forms.ModelForm):
    class Meta:
        model = PoolEvent
        fields = [
            "event_type",
            "day_of_week",
            "name",
            "instructor",
            "start_time",
            "end_time",
            "lane_start",
            "lane_end",
        ]

    def clean(self):
        cleaned = super().clean()

        day = cleaned.get("day_of_week")
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        lane_start = cleaned.get("lane_start")
        lane_end = cleaned.get("lane_end")

        if not all([day, start, end, lane_start, lane_end]):
            return cleaned

        # 🔥 konflikt validation
        qs = PoolEvent.objects.filter(day_of_week=day)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        for event in qs:
            overlap = not (end <= event.start_time or start >= event.end_time)

            lane_overlap = not (
                lane_end < event.lane_start
                or lane_start > event.lane_end
            )

            if overlap and lane_overlap:
                raise forms.ValidationError(
                    f"Konflikt z: {event.name} ({event.start_time}-{event.end_time})"
                )

        return cleaned
