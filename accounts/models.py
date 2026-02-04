from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class Area(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=30,
        unique=True
    )
    def __str__(self):
        return self.name
    

class Role(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class User(AbstractUser):
    username = None  # USUWAMY username
    email = models.EmailField(unique=True)

    area = models.ForeignKey(Area, on_delete=models.PROTECT)
    phone = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'role')


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
        upload_to="area_messages/",
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