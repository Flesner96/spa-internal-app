from django.db import models
from django.conf import settings
import time

def area_message_upload_path(instance, filename):
    area_code = instance.area.code
    ts = int(time.time())
    return f"area_messages/{area_code}/{ts}_{filename}"

class AreaMessage(models.Model):
    area = models.ForeignKey(
        "accounts.Area",
        on_delete=models.CASCADE,
        related_name="messages"
    )

    author = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="area_messages",
    null=False,
    blank=False,
)

    content = models.TextField()

    attachment = models.FileField(
        upload_to=area_message_upload_path,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # edycja
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} | {self.created_at:%Y-%m-%d %H:%M}"
    


class AreaMessageReply(models.Model):
    message = models.OneToOneField(
        AreaMessage,
        on_delete=models.CASCADE,
        related_name="reply",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to #{self.message.id}"
  