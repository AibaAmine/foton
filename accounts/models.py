import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, email, full_name, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_status", "active")
        extra_fields.setdefault("status", "active")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, email, full_name, password, **extra_fields)


class Users(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    is_email_verified = models.BooleanField(default=False)
    account_status = models.CharField(max_length=50)
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50)

    username = None
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["email", "full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Wallet(models.Model):
    wallet_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet - {self.user.email}"


class OTPVerification(models.Model):

    PURPOSE_CHOICES = [
        ("email_verification", "Email Verification"),
        ("password_reset", "Password Reset"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name="otp_verifications",
        null=True,
        blank=True,
    )
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"
