from django.urls import path
from .views import sendMoneyView

urlpatterns = [
    path("send/", sendMoneyView.as_view(), name="send-money"),
]
