from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Users, Wallet


@receiver(post_save, sender=Users)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance, balance=0.00)
