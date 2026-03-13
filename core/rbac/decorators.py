from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


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