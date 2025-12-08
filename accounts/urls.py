from django.urls import path
from .views import (
    UserLoginAPiView,
    PasswordResetRequestView,
    PsswordRestVerifyView,
    PasswordResetConfirmView,
    WalletView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
)

urlpatterns = [
    path("login/", UserLoginAPiView.as_view(), name="user-login"),
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path("logout", LogoutView.as_view(), name="user-logout"),
    path(
        "password-reset/verify/",
        PsswordRestVerifyView.as_view(),
        name="password-reset-verify",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("wallet/", WalletView.as_view(), name="wallet-detail"),
    path("profile/", ProfileView.as_view(), name="profile-detail"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
