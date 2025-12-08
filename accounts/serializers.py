from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wallet, Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "email",
            "phone",
            "avatar",
            "address",
            "city",
            "agency_name",
        ]

    def validate_avatar(self, value):
        if value:
            limit_mb = 2
            if value.size > limit_mb * 1024 * 1024:
                raise serializers.ValidationError(
                    f"File too large. Size should not exceed {limit_mb} MB."
                )

            if not value.name.lower().endswith((".png", ".jpg", ".jpeg")):
                raise serializers.ValidationError(
                    "Unsupported file format. Please upload a JPEG or PNG image."
                )
        return value


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            representation["avatar"] = instance.avatar.url
        return representation


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = ["balance", "last_updated"]


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)


class PasswordRestRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class PasswordRestVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=5, min_length=5)


class PasswordRestConfimSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long"
            )
        return value
