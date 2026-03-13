from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from .capabilities import Capability

ROLE_CAPABILITIES = {
    "BS": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.EDIT_SAUNA_ATTENDANCE,
        Capability.VIEW_CLASSES,
        Capability.VIEW_BALANCE,
        Capability.CREATE_BALANCE,
        Capability.VIEW_VOUCHERS,
        Capability.CREATE_VOUCHERS,
        Capability.EDIT_VOUCHERS,
        Capability.REDEEM_VOUCHERS,
        Capability.MPV_TRANSACTIONS,
        Capability.EXTEND_VOUCHERS,
        Capability.VIEW_REPORTS,
        Capability.CREATE_SHIFT_REPORT,
        Capability.VIEW_SCHEDULE,
    },
    "ASup": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.EDIT_SAUNA_ATTENDANCE,
        Capability.IMPORT_SAUNAS,
        Capability.REPLY_NOTEBOOK,
        Capability.BALANCE_HISTORY,
        Capability.VIEW_BALANCE,
        Capability.CREATE_BALANCE,
        Capability.VIEW_VOUCHERS,
        Capability.CREATE_VOUCHERS,
        Capability.EDIT_VOUCHERS,
        Capability.REDEEM_VOUCHERS,
        Capability.MPV_TRANSACTIONS,
        Capability.EXTEND_VOUCHERS,
        Capability.EDIT_AREA_INFO,
        Capability.VIEW_REPORTS,
        Capability.VIEW_SHIFT_REPORT_LIST,
        Capability.VIEW_SHIFT_REPORT_DETAIL,
        Capability.COMPARE_SHIFT_REPORTS,
        Capability.VIEW_SCHEDULE,
    },
    "Ma": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.REPLY_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.VIEW_VOUCHERS,
        Capability.EXTEND_VOUCHERS,
        Capability.VIEW_SCHEDULE,
    },
    "BD": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.VIEW_CLASSES,
        Capability.MANAGE_CLASSES,
        Capability.REPLY_NOTEBOOK,
        Capability.VIEW_VOUCHERS,
        Capability.EXTEND_VOUCHERS,
        Capability.VIEW_VOUCHER_LOGS,
        Capability.MANAGE_USERS,
        Capability.VIEW_SCHEDULE,
    },
}
CAPABILITY_AREA_SCOPE = {
    Capability.IMPORT_SAUNAS: {"SA"},
    Capability.EDIT_SAUNA_ATTENDANCE: {"SA"},
    Capability.VIEW_BALANCE: {"RC"},
    Capability.CREATE_BALANCE: {"RC"},
    Capability.BALANCE_HISTORY: {"RC"},
    Capability.VIEW_VOUCHERS: {"RC", "BD"},
    Capability.CREATE_VOUCHERS: {"RC", "BD"},
    Capability.EDIT_VOUCHERS: {"RC", "BD"},
    Capability.EXTEND_VOUCHERS: {"RC", "BD"},
    Capability.REDEEM_VOUCHERS: {"RC", "BD"},
    Capability.MPV_TRANSACTIONS: {"RC", "BD"},
    Capability.VIEW_VOUCHER_LOGS: {"RC", "BD"},

    Capability.CREATE_SHIFT_REPORT: {"RC"},
    Capability.VIEW_SHIFT_REPORT_LIST: {"RC"},
    Capability.VIEW_SHIFT_REPORT_DETAIL: {"RC"},
    Capability.COMPARE_SHIFT_REPORTS: {"RC"},
}

def user_has_capability(user, capability: str) -> bool:

    if not user.is_authenticated:
        return False

    if "SysA" in user.role_codes:
        return True

    # ---- cache capabilities ----
    if not hasattr(user, "_cached_capabilities"):

        caps = set()

        for role in user.role_codes:
            caps.update(ROLE_CAPABILITIES.get(role, set()))

        user._cached_capabilities = caps

    if capability not in user._cached_capabilities:
        return False

    # ---- area scope ----
    allowed_areas = CAPABILITY_AREA_SCOPE.get(capability)

    if not allowed_areas:
        return True

    if not user.area:
        return False

    return user.area.code in allowed_areas


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
