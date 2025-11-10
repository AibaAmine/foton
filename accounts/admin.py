from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Users, Wallet, OTPVerification


class CustomUserAdmin(BaseUserAdmin):
    model = Users
    list_display = ['phone', 'email', 'full_name', 'is_staff', 'account_status', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'account_status']
    search_fields = ['phone', 'email', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('email', 'full_name')}),
        ('Status', {'fields': ('account_status', 'status', 'is_email_verified', 'last_active_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'full_name', 'password1', 'password2', 'account_status'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['wallet_id', 'user', 'balance', 'last_updated']
    search_fields = ['user__phone', 'user__email']
    list_filter = ['last_updated']


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'purpose', 'is_used', 'created_at', 'expiry_date']
    search_fields = ['user__phone', 'code']
    list_filter = ['is_used', 'purpose', 'created_at']


admin.site.register(Users, CustomUserAdmin)
