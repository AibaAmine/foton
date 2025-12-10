import random
import string
from transactions.models import Transaction, MoneyRequester
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from accounts.models import Wallet


from decimal import Decimal


class TransactionService:

    @staticmethod
    def calculate_fee(amount):
        """
        Calculates the fee based on the amount range.
        """
        amount = Decimal(str(amount))

        if 1000 <= amount <= 5000:
            return Decimal("100.00")
        elif 5000 < amount <= 10000:
            return Decimal("200.00")
        elif 10000 < amount <= 15000:
            return Decimal("300.00")
        elif 15000 < amount <= 20000:
            return Decimal("400.00")
        elif 20000 < amount <= 30000:
            return Decimal("500.00")
        elif 30000 < amount <= 50000:
            return Decimal("600.00")
        elif 50000 < amount <= 70000:
            return Decimal("700.00")
        elif 70000 < amount <= 100000:
            return Decimal("800.00")
        else:

            if amount < 1000:
                return Decimal("0.00")

            return amount * Decimal("0.01")

    @staticmethod
    def generate_transfer_code():
        while True:
            code = "".join(random.choices(string.digits, k=10))
            if not Transaction.objects.filter(transfer_code=code).exists():
                return code

    @staticmethod
    def create_send_transaction(agent, sender_data, recipient_data, amount, fee):
        total_required = amount + fee

        with transaction.atomic():
            # We fetch the wallet specifically to lock it
            try:
                agent_wallet = Wallet.objects.select_for_update().get(user=agent)
            except Wallet.DoesNotExist:
                raise ValidationError("Agent does not have a wallet.")

            # Insufficient funds check removed to allow negative balance (overdraft)
            # if agent_wallet.balance < total_required:
            #     raise ValidationError("Insufficient funds in agent wallet.")

            # 2. Handle Sender
            sender, _ = MoneyRequester.objects.update_or_create(
                phone_number=sender_data["phone_number"],
                defaults={
                    "first_name": sender_data["first_name"],
                    "last_name": sender_data["last_name"],
                    # Only update ID if it's present in the data
                    **(
                        {"national_id_number": sender_data["national_id_number"]}
                        if sender_data.get("national_id_number")
                        else {}
                    ),
                },
            )

            # 3. Handle Recipient
            recipient, _ = MoneyRequester.objects.update_or_create(
                phone_number=recipient_data["phone_number"],
                defaults={
                    "first_name": recipient_data["first_name"],
                    "last_name": recipient_data["last_name"],
                },
            )

            # 4. Create Transaction
            transfer_code = TransactionService.generate_transfer_code()

            new_txn = Transaction.objects.create(
                amount=amount,
                fee=fee,
                status=Transaction.Status.PENDING,
                type=Transaction.Type.TRANSFER,
                transfer_code=transfer_code,
                initiating_agent=agent,
                sender_person=sender,
                recipient_person=recipient,
            )

            # 5. Deduct from Wallet
            agent_wallet.balance -= total_required
            agent_wallet.save()

            return new_txn

    @staticmethod
    def lookup_transaction(transfer_code=None, phone_number=None, last_name=None):

        qs = Transaction.objects.filter(
            status__in=[Transaction.Status.PENDING, Transaction.Status.EXPIRED]
        )

        if transfer_code:
            return qs.filter(
                transfer_code=transfer_code
            ).first()  # we used .first() so if not found its returning None not craching the app

        if phone_number and last_name:
            return qs.filter(
                recipient_person__phone_number=phone_number,
                recipient_person__last_name__iexact=last_name,
            ).first()

        return None

    @staticmethod
    def claim_transaction(agent, transaction_id, national_id_number=None):

        with transaction.atomic():
            try:
                # LOCK the row. No one else can touch this transaction until we finish. (for the risk of clicking multiple times etc..)
                txn = Transaction.objects.select_for_update().get(pk=transaction_id)
            except Transaction.DoesNotExist:
                raise ValidationError("Transaction not found.")

            # expiring logic starts
            is_refund = False

            if txn.status == Transaction.Status.EXPIRED:
                # if we are here that mean that its expired trasaction and its refund situation
                is_refund = True

            elif txn.status != Transaction.Status.PENDING:
                raise ValidationError("Transaction has already been processed.")

            if national_id_number:

                person = txn.sender_person if is_refund else txn.recipient_person
                person.national_id_number = national_id_number
                person.save()

            # The agent gave CASH to the customer, so we give DIGITAL money to the agent.
            agent_wallet = getattr(agent, "wallet", None)
            if not agent_wallet:
                raise ValidationError("Agent does not have a wallet.")

            # Reimburse the agent
            agent_wallet.balance += txn.amount
            agent_wallet.save()

            #  Update Transaction Status
            txn.status = Transaction.Status.COMPLETED
            txn.receiving_agent = agent
            txn.claimed_at = timezone.now()
            txn.memo = "Refunded to Sender" if is_refund else "Claimed by Recipient"
            txn.save()

            return txn
