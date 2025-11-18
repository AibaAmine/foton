from django.conf import settings
from twilio.rest import Client


class SMSBackend:
        
    def send_sms(self, phone_number, message):
        raise NotImplementedError("Subclasses must implement send_sms method")


class ConsoleSMSBackend(SMSBackend):
    """local test"""
    
    def send_sms(self, phone_number, message):
        print("\n" + "="*50)
        print(f"[SMS CONSOLE BACKEND]")
        print(f"To: {phone_number}")
        print(f"Message: {message}")
        print("="*50 + "\n")
        return True


class TwilioSMSBackend(SMSBackend):
    """SMS backend that sends real SMS via Twilio"""
    
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_sms(self, phone_number, message):
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"Twilio SMS Error: {str(e)}")
            return False


def get_sms_backend():
    """Factory function to get appropriate SMS backend"""
    if settings.SMS_BACKEND == 'console':
        return ConsoleSMSBackend()
    elif settings.SMS_BACKEND == 'twilio':
        print("here")
        return TwilioSMSBackend()
    else:
        raise ValueError(f"Unknown SMS backend: {settings.SMS_BACKEND}")