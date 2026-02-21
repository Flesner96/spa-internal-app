from django.urls import path
from .views import voucher_search_view, voucher_create_view, voucher_redeem_view, voucher_edit_view, voucher_extend_view, voucher_transaction_view, voucher_logs_view, voucher_list_view

app_name = "vouchers"

urlpatterns = [ 
    path ("", voucher_search_view, name="voucher_search"),
    path("create/", voucher_create_view , name="voucher_create"),
    path(
    "<int:pk>/redeem/",
    voucher_redeem_view,
    name="voucher_redeem",
    ),
    path(
    "<int:pk>/edit/",
    voucher_edit_view,
    name="voucher_edit",
    ),
    path("<int:pk>/extend/", voucher_extend_view, name="voucher_extend"),
    path("<int:pk>/transaction/", voucher_transaction_view, name="voucher_transaction"),
    path("logs/", voucher_logs_view, name="voucher_logs"),
    path("all/", voucher_list_view, name="voucher_list"),
]