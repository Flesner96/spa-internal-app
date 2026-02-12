from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


class Capability:
    VIEW_NOTEBOOK = "view_notebook"
    POST_NOTEBOOK = "post_notebook"
    EDIT_NOTEBOOK = "edit_notebook"
    MANAGE_USERS = "manage_users"
    IMPORT_SAUNAS = 'import_saunas'
    VIEW_SAUNAS = "view_saunas"
    EDIT_SAUNA_ATTENDANCE = "edit_sauna_attendance"
    VIEW_CLASSES = "view_classe"
    MANAGE_CLASSES = "manage_classes" 
    REPLY_NOTEBOOK = "reply_notebook"    

ROLE_CAPABILITIES = {
    "BS": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.EDIT_SAUNA_ATTENDANCE,
        Capability.VIEW_CLASSES,
    },
    "ASup": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.EDIT_SAUNA_ATTENDANCE,
        Capability.IMPORT_SAUNAS,
        Capability.REPLY_NOTEBOOK,
    },
    "Ma": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.REPLY_NOTEBOOK,
    },
    "BD": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.VIEW_CLASSES,
        Capability.MANAGE_CLASSES,
        Capability.REPLY_NOTEBOOK,
    },
}


def user_has_capability(user, capability: str) -> bool:
    if not user.is_authenticated:
        return False

    if "SysA" in user.role_codes:
        return True

    for role in user.role_codes:
        if capability in ROLE_CAPABILITIES.get(role, set()):
            return True

    return False


def require_capability(capability):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("login")

            if not request.user.can(capability):
                return HttpResponseForbidden()

            return view_func(request, *args, **kwargs)

        return _wrapped
    return decorator
