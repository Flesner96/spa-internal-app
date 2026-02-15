from django.urls import path
from . import views

urlpatterns = [ 
    path ("", views.voucher_search.view, name="voucher_search"),
    path("create", views.voucher_create_view , name="voucher_create"),

]