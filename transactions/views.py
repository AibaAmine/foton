from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from decimal import Decimal

from .serializers import (
    PersonSerializer,
    SendMoneySerializer,
    ReceiveMoneyLookupSerializer,
    RecieveMoneyClaimSerializer,
)
from services.transactions_services import TransactionService
from services.notification_service import NotificationService


class sendMoneyView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendMoneySerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data

            amount = data["amount"]
            fee = amount * Decimal("0.01")

            try:
                transaction = TransactionService.create_send_transaction(
                    agent=request.user,
                    sender_data=data["sender"],
                    recipient_data=data["recipient"],
                    amount=amount,
                    fee=fee,
                )

                NotificationService.send_transfer_sms(transaction)

                return Response(
                    {
                        "message": "Transaction successful",
                        "transfer_code": transaction.transfer_code,
                        "transaction_id": transaction.transaction_id,
                        "fee_charged": fee,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Error in SendMoneyView: {e}")
                return Response(
                    {"error": "An internal error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiveLookupView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReceiveMoneyLookupSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data

            transaction = TransactionService.lookup_transaction(
                transfer_code=data.get("transfer_code"),
                phone_number=data.get("phone_number"),
                last_name=data.get("last_name"),
            )

            if transaction:
                return Response(
                    {
                        "transaction_id": transaction.transaction_id,
                        "amount": transaction.amount,
                        "sender": {
                            "name": f"{transaction.sender_person.first_name} {transaction.sender_person.last_name}",
                            "phone": transaction.sender_person.phone_number,
                        },
                        "recipient": {
                            "name": f"{transaction.recipient_person.first_name} {transaction.recipient_person.last_name}",
                            "phone": transaction.recipient_person.phone_number,
                        },
                        "created_at": transaction.created_at,
                        "status": transaction.status,
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"error": "Transaction not found or already claimed."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiveClaimView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RecieveMoneyClaimSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            try:
                txn = TransactionService.claim_transaction(
                    agent=request.user,
                    transaction_id=data["transaction_id"],
                    national_id_number=data.get("national_id_number"),
                )

                return Response(
                    {
                        "message": "Transaction claimed successfully.",
                        "transaction_id": txn.transaction_id,
                        "amount": txn.amount,
                        "claimed_at": txn.claimed_at,
                    },
                    status=status.HTTP_200_OK,
                )

            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Error in ReceiveClaimView: {e}")
                return Response(
                    {"error": "Internal error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
