from django.urls import path
from .views import voucher_search_view, voucher_create_view

urlpatterns = [ 
    path ("", voucher_search_view, name="voucher_search"),
    path("create/", voucher_create_view , name="voucher_create"),

]