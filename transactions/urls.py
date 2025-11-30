from django.urls import path
from .views import sendMoneyView, ReceiveLookupView, ReceiveClaimView

urlpatterns = [
    path("send/", sendMoneyView.as_view(), name="send-money"),
    path("receive/lookup/", ReceiveLookupView.as_view(), name="receive-lookup"),
    path("receive/claim/", ReceiveClaimView.as_view(), name="receive-claim"),
]
