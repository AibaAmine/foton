import random
import string
from transactions.models import Transaction,MoneyRequester
from django.core.exceptions import ValidationError
from django.db import transaction


class TransactionService:

    @staticmethod
    def generate_transfer_code():
        while True:
            code = "".join(random.choices(string.digits, k=10))
            if not Transaction.objects.filter(transfer_code=code).exists():
                return code

    @staticmethod
    def create_send_transaction(agent, sender_data, recipient_data, amount, fee):
        total_required = amount + fee
        agent_wallet = getattr(agent, "wallet", None)

        if not agent_wallet:
            raise ValidationError("Agent does not have a wallet.")

        if agent_wallet.balance < total_required:
            raise ValidationError("Insufficient funds in agent wallet.")

        with transaction.atomic():
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
