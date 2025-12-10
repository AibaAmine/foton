from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from .serializers import (
    PersonSerializer,
    SendMoneySerializer,
    ReceiveMoneyLookupSerializer,
    RecieveMoneyClaimSerializer,
    TransactionHistorySerializer,
    UserLookupSerializer,
    TransactionDetailSerializer,
)
from services.transactions_services import TransactionService
from services.notification_service import NotificationService
from .models import IdempotencyLog, Transaction, MoneyRequester
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from django.db import IntegrityError, transaction
from accounts.views import User


class sendMoneyView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # If this fails (IntegrityError), it means the key exists (duplicate request).
                log_entry, created = IdempotencyLog.objects.get_or_create(
                    key=idempotency_key,
                    defaults={"user": request.user, "status": "PROCESSING"},
                )
        except IntegrityError:
            log_entry = IdempotencyLog.objects.get(key=idempotency_key)
            created = False

        if not created:
            if log_entry.status == "PROCESSING":
                return Response(
                    {"error": "Transaction is currently being processed. Please wait."},
                    status=status.HTTP_409_CONFLICT,
                )
            return Response(log_entry.response_body, status=log_entry.response_status)

        serializer = SendMoneySerializer(data=request.data)

        if not serializer.is_valid():
            log_entry.status = "FAILED"
            log_entry.response_body = serializer.errors
            log_entry.response_status = status.HTTP_400_BAD_REQUEST
            log_entry.save()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data

            amount = data["amount"]
            fee = TransactionService.calculate_fee(amount)

            new_txn = TransactionService.create_send_transaction(
                agent=request.user,
                sender_data=data["sender"],
                recipient_data=data["recipient"],
                amount=amount,
                fee=fee,
            )

            response_data = {
                "message": "Transaction successful",
                "transfer_code": new_txn.transfer_code,
                "transaction_id": str(new_txn.transaction_id),
                "fee_charged": float(fee),
            }
            response_status = status.HTTP_201_CREATED

            log_entry.response_body = response_data
            log_entry.response_status = status.HTTP_201_CREATED
            log_entry.status = "COMPLETED"
            log_entry.save()

            try:
                NotificationService.send_transfer_sms(new_txn)
            except Exception as e:
                print(f"SMS Failed (Non-blocking): {e}")

            return Response(response_data, status=response_status)

        except ValidationError as e:
            error_resp = {"error": str(e)}
            log_entry.response_body = error_resp
            log_entry.response_status = status.HTTP_400_BAD_REQUEST
            log_entry.status = "FAILED"
            log_entry.save()
            return Response(error_resp, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Critical Error: {e}")
            # Internal Error
            error_resp = {"error": "An internal error occurred."}
            log_entry.response_body = error_resp
            log_entry.response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            log_entry.status = "FAILED"
            log_entry.save()
            return Response(error_resp, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class TransactionDetailView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(transaction_id=transaction_id)

            # Ensure the requesting user is either the initiating or receiving agent
            if (
                transaction.initiating_agent != request.user
                and transaction.receiving_agent != request.user
            ):
                return Response(
                    {"error": "You do not have permission to view this transaction."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = TransactionDetailSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class TransactionHistoryView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Filter transactions where user is sender or receiver
        transactions = Transaction.objects.filter(
            Q(initiating_agent=user) | Q(receiving_agent=user)
        ).order_by("-created_at")

        # Pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(transactions, request)

        serializer = TransactionHistorySerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class UserlookupView(views.APIView):

    def post(self, request):

        serializer = UserLookupSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone = serializer.validated_data["phone_number"]

            agent = User.objects.filter(phone=phone).first()

            if agent:
                return Response(
                    {
                        "error": "Cannot send consumer transfer to a registered Foton Agent's number.",
                        "type": "agent_conflict",
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            customer = MoneyRequester.objects.filter(phone_number=phone).first()
            if customer:
                return Response(
                    {
                        "full_name": f"{customer.first_name} {customer.last_name}",
                        "type": "Customer",
                        "exists_in_history": True,
                        "message": "Customer identified from history.",
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "message": "New customer. Please fill in details.",
                    "exists_in_history": False,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpireTransactionsView(views.APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        now = timezone.now()

        expired_qs = Transaction.objects.filter(
            status=Transaction.Status.PENDING, expires_at__lte=now
        )

        count = 0
        if expired_qs.exists():
            for txn in expired_qs:
                txn.status = Transaction.Status.EXPIRED
                txn.save()

                try:
                    NotificationService.send_refund_sms(txn)
                except Exception as e:
                    print(f"SMS Failed: {e}")

                count += 1

        return Response(
            {"message": "Cleanup executed", "expired_count": count},
            status=status.HTTP_200_OK,
        )


class CalculateFeeView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        amount = request.query_params.get("amount")
        if not amount:
            return Response(
                {"error": "Amount parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount_decimal = Decimal(amount)
            fee = TransactionService.calculate_fee(amount_decimal)
            total = amount_decimal + fee

            return Response(
                {
                    "amount": float(amount_decimal),
                    "fee": float(fee),
                    "total": float(total),
                }
            )
        except Exception as e:
            return Response(
                {"error": "Invalid amount format."},
                status=status.HTTP_400_BAD_REQUEST,
            )
