from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    UserLoginSerializer,
    
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

# Create your views here.

class UserLoginAPiView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        password = serializer.validated_data["password"]
        user = authenticate(phone = phone, password=password)

        if user:
            access_token = AccessToken.for_user(user)  # Generate access token
            refresh_token = RefreshToken.for_user(user)  # Generate refresh token

            return Response(
                {
                    "access": str(access_token),
                    "refresh": str(refresh_token),
                }
            )
        return Response(
            {"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

