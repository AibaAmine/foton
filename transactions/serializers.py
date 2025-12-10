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


class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = [
            "transaction_id",
            "amount",
            "fee",
            "created_at",
            "status",
            "type",
            "memo",
            "transfer_code",
            "claimed_at",
            "initiating_agent",
            "receiving_agent",
            "sender_person",
            "recipient_person",
            "expires_at",
        ]


class TransactionHistorySerializer(serializers.ModelSerializer):
    direction = serializers.SerializerMethodField()
    other_party_name = serializers.SerializerMethodField()
    other_party_phone = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "transaction_id",
            "amount",
            "created_at",
            "status",
            "direction",
            "other_party_name",
            "other_party_phone",
            "transfer_code",
        ]

    def get_direction(self, obj):
        user = self.context["request"].user
        if obj.initiating_agent == user:
            return "sent"
        return "received"

    def get_other_party_name(self, obj):
        user = self.context["request"].user
        if obj.initiating_agent == user:
            return f"{obj.recipient_person.first_name} {obj.recipient_person.last_name}"
        return f"{obj.sender_person.first_name} {obj.sender_person.last_name}"

    def get_other_party_phone(self, obj):
        user = self.context["request"].user
        if obj.initiating_agent == user:
            return obj.recipient_person.phone_number
        return obj.sender_person.phone_number


class UserLookupSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
