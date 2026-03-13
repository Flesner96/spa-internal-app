from .models import AppLog


def log_action(user, action, obj=None, details=""):

    AppLog.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__ if obj else "",
        object_id=obj.id if obj else None,
        details=details,
    )