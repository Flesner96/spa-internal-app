"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from accounts.forms import EmailAuthenticationForm
from accounts.views import dashboard_view, root_view, profile_view, ForcedPasswordChangeView, user_create_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # ROOT = LOGIN
    path("", root_view, name="root"),
    path("dashboard/", dashboard_view, name="dashboard"),
    # ACCOUNT APP
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=EmailAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
    "password-change/",
    ForcedPasswordChangeView.as_view(),
    name="password_change",
    ),
    path(
    "password-change/done/",
    auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/password_change_done.html",
    ),
    name="password_change_done",
    ),
    path("admin/", admin.site.urls),
    path("profile/", profile_view, name="profile"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    path("users/create/", user_create_view, name="user_create"),
    path("saunas/", include("saunas.urls")),
    path("notebook/", include("notebook.urls")),
    path("classes/", include("classes.urls")),
    path("balance/", include("balance.urls")),
    # path("vouchers/", include("vouchers.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
