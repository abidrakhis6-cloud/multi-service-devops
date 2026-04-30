from django.contrib import admin
from .models import (
    UserProfile, PhoneOTP, Notification, UserSession,
    OAuthToken, SecurityLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'phone_verified', 'preferred_auth_method', 'created_at']
    list_filter = ['phone_verified', 'preferred_auth_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code_masked', 'is_used', 'is_expired', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['phone_number', 'user__username']
    readonly_fields = ['created_at', 'expires_at', 'verified_at']
    
    def otp_code_masked(self, obj):
        return obj.otp_code[:2] + '****' if obj.otp_code else '-'
    otp_code_masked.short_description = 'Code OTP'
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'channel', 'title', 'status', 'created_at']
    list_filter = ['notification_type', 'channel', 'status', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'sent_at', 'delivered_at', 'read_at']
    
    actions = ['mark_as_sent', 'mark_as_delivered', 'mark_as_read']
    
    def mark_as_sent(self, request, queryset):
        for n in queryset:
            n.mark_as_sent()
    mark_as_sent.short_description = "Marquer comme envoyé"
    
    def mark_as_delivered(self, request, queryset):
        for n in queryset:
            n.mark_as_delivered()
    mark_as_delivered.short_description = "Marquer comme livré"
    
    def mark_as_read(self, request, queryset):
        for n in queryset:
            n.mark_as_read()
    mark_as_read.short_description = "Marquer comme lu"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_info', 'is_active', 'is_trusted', 'created_at']
    list_filter = ['is_active', 'is_trusted', 'created_at']
    search_fields = ['user__username', 'session_key', 'ip_address']
    readonly_fields = ['created_at', 'last_activity', 'ended_at']
    
    actions = ['end_session']
    
    def end_session(self, request, queryset):
        for s in queryset:
            s.end_session()
    end_session.short_description = "Terminer les sessions"


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'provider_email', 'is_expired', 'created_at']
    list_filter = ['provider', 'created_at']
    search_fields = ['user__username', 'provider_user_id', 'provider_email']
    readonly_fields = ['created_at', 'updated_at']
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'ip_address', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

