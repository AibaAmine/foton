import uuid
from django.db import models
from accounts.models import Users


class MoneyRequester(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    national_id_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Transaction(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Type(models.TextChoices):
        TRANSFER = "transfer", "Transfer"
        DEPOSIT = "deposit", "Deposit"
        WITHDRAWAL = "withdrawal", "Withdrawal"


    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Status.choices)
    type = models.CharField(max_length=50, choices=Type.choices)
    memo = models.TextField(blank=True, null=True)
    transfer_code = models.CharField(max_length=255, unique=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    initiating_agent = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="initiated_transactions"
    )
    receiving_agent = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name="received_agent_transactions",
        null=True,
        blank=True,
    )

    sender_person = models.ForeignKey(
        MoneyRequester, on_delete=models.CASCADE, related_name="sent_transactions"
    )
    recipient_person = models.ForeignKey(
        MoneyRequester, on_delete=models.CASCADE, related_name="received_transactions"
    )

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.type}"
