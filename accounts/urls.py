from django.urls import path
from .views import (
    UserLoginAPiView,
    PasswordResetRequestView,
    PsswordRestVerifyView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('login/', UserLoginAPiView.as_view(), name='user-login'),
    
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/verify/', PsswordRestVerifyView.as_view(), name='password-reset-verify'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]