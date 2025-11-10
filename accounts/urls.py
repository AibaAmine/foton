from django.urls import path
from .views import UserLoginAPiView

urlpatterns = [
    path('login/', UserLoginAPiView.as_view(), name='login'),
]
