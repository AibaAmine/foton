from django.contrib import admin
from .models import Transaction, MoneyRequester


@admin.register(MoneyRequester)
class MoneyRequesterAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'phone_number', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone_number', 'user__phone']
    list_filter = ['created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'type', 'amount', 'fee', 'status', 'initiating_agent', 'created_at']
    search_fields = ['transaction_id', 'transfer_code', 'initiating_agent__phone', 'receiving_agent__phone']
    list_filter = ['type', 'status', 'created_at']
    readonly_fields = ['created_at', 'claimed_at']
