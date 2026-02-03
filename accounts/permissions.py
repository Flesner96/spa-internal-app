from functools import wraps
from django.shortcuts import redirect

def require_role(role_code):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):

            # 🔐 MUSI być zalogowany
            if not request.user.is_authenticated:
                return redirect("login")

            has_role = request.user.userrole_set.filter(
                role__code=role_code
            ).exists()

            if not has_role:
                return redirect("dashboard")

            return view_func(request, *args, **kwargs)

        return _wrapped
    return decorator
