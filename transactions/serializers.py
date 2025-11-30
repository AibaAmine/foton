from rest_framework import serializers
from .models import Transaction


class PersonSerializer(serializers.Serializer):

    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)

    national_id_number = serializers.CharField(
        max_length=50, required=False, allow_blank=True
    )


class SendMoneySerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    sender = PersonSerializer()
    recipient = PersonSerializer()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value


class ReceiveMoneyLookupSerializer(serializers.Serializer):

    transfer_code = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):

        code = data.get("transfer_code")
        phone = data.get("phone_number")
        name = data.get("last_name")

        if code:
            return data

        if phone and name:
            return data

        raise serializers.ValidationError(
            "You must provide either a Transfer Code OR both Phone Number and Last Name "
        )


class RecieveMoneyClaimSerializer(serializers.Serializer):
    transaction_id = serializers.UUIDField()
    national_id_number = serializers.CharField(required=False, allow_blank=True)
