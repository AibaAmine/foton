from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
