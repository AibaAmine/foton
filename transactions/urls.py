from django.urls import path
from .views import (
    sendMoneyView,
    ReceiveLookupView,
    ReceiveClaimView,
    TransactionHistoryView,
    UserlookupView,
    ExpireTransactionsView,
    CalculateFeeView,
)

urlpatterns = [
    path("send/", sendMoneyView.as_view(), name="send-money"),
    path("receive/lookup/", ReceiveLookupView.as_view(), name="receive-lookup"),
    path("receive/claim/", ReceiveClaimView.as_view(), name="receive-claim"),
    path("history/", TransactionHistoryView.as_view(), name="transaction-history"),
    path("lookup-user/", UserlookupView.as_view(), name="lookup-user"),
    path("expire-trigger/", ExpireTransactionsView.as_view(), name="expire-trigger"),
    path("calculate-fee/", CalculateFeeView.as_view(), name="calculate-fee"),
]
