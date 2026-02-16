from django.urls import path
from .views import voucher_search_view, voucher_create_view, voucher_redeem_view, voucher_edit_view

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
]