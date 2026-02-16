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
    VIEW_BALANCE = "view_balance"
    CREATE_BALANCE = "create_balance"    
    BALANCE_HISTORY = "balance_history"
    VIEW_VOUCHERS = "view_vouchers"
    CREATE_VOUCHERS = "create_vouchers"
    EDIT_VOUCHERS = "edit_vouchers"
    EXTEND_VOUCHERS = "extend_vouchers"
    REDEEM_VOUCHERS = "redeem_vouchers"
    MPV_TRANSACTIONS = "mpv_transactions"
    VIEW_VOUCHER_LOGS = "view_voucher_logs"



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
    },
    "Ma": {
        Capability.VIEW_NOTEBOOK,
        Capability.POST_NOTEBOOK,
        Capability.VIEW_SAUNAS,
        Capability.REPLY_NOTEBOOK,
        Capability.VIEW_VOUCHERS,
        Capability.EXTEND_VOUCHERS,
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
