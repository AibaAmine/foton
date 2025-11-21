import random
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
from django.utils import timezone
from accounts.models import OTPVerification, Users
from accounts.sms_backends import get_sms_backend
import jwt

print(settings.SECRET_KEY)


def generate_otp():
    return str(random.randint(10000, 99999))


def generate_rest_token(user_id, otp_id):
    payload = {
        "user_id": str(user_id),
        "otp_id": str(otp_id),
        "purpose": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1),  # Add expiration (1 hour)
        "iat": datetime.utcnow(),  # Add issued at time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def verify_rest_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        print(f" +++++++++++++++++++++++++ payload is : { payload }")

        if payload.get("purpose") != "password_reset":
            return False, None

        return True, payload
    except jwt.ExpiredSignatureError:
        print("here expired")
        return False, None
    except jwt.InvalidTokenError:
        print("here invalid")
        return False, None


def create_password_reset_otp(phone):

    try:
        user = Users.objects.get(phone=phone)

    except Users.DoesNotExist:
        return False, "Phone number not registered."

    # invalidate previous OTPs
    OTPVerification.objects.filter(
        user=user,
        purpose="password_reset",
        is_used=False,
    ).update(is_used=True)

    # Generate OTP
    otp_code = generate_otp()

    # Set expiration (10 minutes from now)
    expiry = timezone.now() + timedelta(minutes=10)

    # Create OTP record
    otp = OTPVerification.objects.create(
        user=user,
        code=otp_code,
        expiry_date=expiry,
        purpose="password_reset",
        is_used=False,
        is_verified=False,
    )

    # Send SMS
    sms_backend = get_sms_backend()
    message = f"Your Foton password reset OTP is: {otp_code}. Valid for 10 minutes."

    success = sms_backend.send_sms(phone, message)

    if success:
        return True, "OTP sent successfully"
    else:
        otp.delete()  # Clean up if SMS failed
        return False, "Failed to send OTP"


def verify_password_reset_otp(phone, otp_code):

    try:

        user = Users.objects.get(phone=phone)
        otp = OTPVerification.objects.get(
            user=user,
            code=otp_code,
            purpose="password_reset",
            is_used=False,
            is_verified=False,
        )

        # Check if expired
        if timezone.now() > otp.expiry_date:
            return False, "OTP has expired", None

        otp.is_verified = True
        otp.save()

        # generate jwt reset token
        reset_token = generate_rest_token(user.id, otp.id)

        return True, "OTP verified successfully", reset_token

    except (OTPVerification.DoesNotExist, Users.DoesNotExist):
        return False, "Invalid OTP", None


def reset_user_password(reset_token, new_password):

    # Verify OTP first
    valid, payload = verify_rest_token(reset_token)
    print(f"payload = {payload}   is valid = {valid}")

    if not valid:
        return False, "Invalid or expired reset token"

    try:
        user_id = payload.get("user_id")
        otp_id = payload.get("otp_id")

        user = Users.objects.get(id=user_id)
        otp = OTPVerification.objects.get(
            id=otp_id,
            user=user,
            purpose="password_reset",
            is_verified=True,
            is_used=False,
        )

        user.set_password(new_password)
        user.save()

        otp.is_used = True
        otp.save()

        return True, "Password reset successfully"

    except (Users.DoesNotExist, OTPVerification.DoesNotExist):
        return False, "invalid reset token"
