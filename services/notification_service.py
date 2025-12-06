from accounts.sms_backends import get_sms_backend

class NotificationService:

    @staticmethod
    def send_transfer_sms(transaction):
        backend = get_sms_backend()

        recipient_name = transaction.recipient_person.first_name
        sender_name = transaction.sender_person.first_name
        amount = transaction.amount
        code = transaction.transfer_code

        message = (
            f"Foton:  {recipient_name}, vous avez reçu {amount} DZD "
            f"de la part de {sender_name}. "
            f"Votre code de retrait est : {code}"
        )

        # If SMS fails, the money is still moved, we just log the error.
        try:
            backend.send_sms(transaction.recipient_person.phone_number, message)
        except Exception as e:
            print(
                f"Failed to send SMS for transaction {transaction.transaction_id}: {e}"
            )

    @staticmethod
    def send_refund_sms(transaction):
        backend = get_sms_backend()

        sender_name = transaction.sender_person.first_name
        amount = transaction.amount
        code = transaction.transfer_code

        message = (
            f"Foton: {sender_name}, votre transfert de {amount} DZD a expiré. "
            f"Veuillez vous rendre chez un agent pour récupérer votre remboursement. "
            f"Code: {code}"
        )

        try:
            # We send this to the SENDER_PERSON
            backend.send_sms(transaction.sender_person.phone_number, message)
        except Exception as e:
            print(
                f"Failed to send Refund SMS for transaction {transaction.transaction_id}: {e}"
            )
