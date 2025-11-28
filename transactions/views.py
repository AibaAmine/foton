from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from decimal import Decimal

from .serializers import PersonSerializer, SendMoneySerializer
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
