from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from services.account_service import create_password_reset_otp ,verify_password_reset_otp,reset_user_password
from .serializers import (
    UserLoginSerializer,PasswordRestRequestSerializer,PasswordRestConfimSerializer,PasswordRestVerifySerializer,
    WalletSerializer
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


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordRestRequestSerializer
    permission_classes =[AllowAny]
    authentication_classes=[]
    
    def post(self,request):
        
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data["phone"]
        
        success ,message = create_password_reset_otp(phone)
        
        if success:
            return Response({
                "success":True,
                "message":message
            },status=status.HTTP_200_OK
            )
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
class PsswordRestVerifyView(generics.GenericAPIView):
    
    serializer_class = PasswordRestVerifySerializer
    permission_classes = [AllowAny] 
    authentication_classes = []   
    
    
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone = serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]
        
        valid ,message ,reset_token = verify_password_reset_otp(phone,otp)
        
        if valid:
            return Response({
                'success': True,
                'message': message,
                'reset_token': reset_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordRestConfimSerializer
    permission_classes = [AllowAny]
    authentication_classes = [] 

    
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data["reset_token"]
        new_password = serializer.validated_data["new_password"]
        
        success, message = reset_user_password(reset_token, new_password)
        
        if success:
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)


class WalletView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_object(self):
        return self.request.user.wallet
        
           
        
        