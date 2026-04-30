from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
import pyotp
import random


class UserProfile(models.Model):
    """Extension du modèle User avec authentification téléphone et OAuth"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Phone authentication
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
        help_text="Numéro de téléphone format international (+33612345678)"
    )
    phone_verified = models.BooleanField(default=False)
    
    # OAuth providers
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    # Profile info
    avatar_url = models.URLField(blank=True, null=True)
    preferred_auth_method = models.CharField(
        max_length=20,
        choices=[
            ('password', 'Mot de passe'),
            ('phone', 'Téléphone/SMS'),
            ('google', 'Google OAuth'),
            ('facebook', 'Facebook OAuth'),
        ],
        default='password'
    )
    
    # Security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(blank=True, null=True)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile de {self.user.username}"
    
    def is_account_locked(self):
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, minutes=30):
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
    
    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.account_locked_until = None
        self.save()


class PhoneOTP(models.Model):
    """Codes OTP pour authentification par téléphone"""
    phone_number = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='otp_codes')
    
    # Security
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = 3
    is_used = models.BooleanField(default=False)
    
    # Expiration
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Verification
    verified_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'created_at']),
            models.Index(fields=['otp_code', 'is_used']),
        ]
    
    def __str__(self):
        return f"OTP pour {self.phone_number} - {'Vérifié' if self.is_verified() else 'En attente'}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # OTP expire après 10 minutes
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_otp():
        """Génère un code OTP à 6 chiffres"""
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def is_verified(self):
        return self.is_used and self.verified_at is not None
    
    def can_attempt(self):
        return self.attempts < self.max_attempts and not self.is_expired() and not self.is_used
    
    def verify(self, code):
        """Vérifie le code OTP"""
        if not self.can_attempt():
            return False, "Code expiré ou nombre de tentatives dépassé"
        
        self.attempts += 1
        
        if self.otp_code != code:
            self.save()
            remaining = self.max_attempts - self.attempts
            return False, f"Code incorrect. {remaining} tentatives restantes."
        
        if self.is_expired():
            self.save()
            return False, "Code expiré"
        
        self.is_used = True
        self.verified_at = timezone.now()
        self.save()
        return True, "Code vérifié avec succès"


class Notification(models.Model):
    """Système de notifications SMS et Email"""
    NOTIFICATION_TYPES = [
        ('new_message', 'Nouveau message'),
        ('order_update', 'Mise à jour commande'),
        ('appointment_reminder', 'Rappel rendez-vous'),
        ('security_alert', 'Alerte de sécurité'),
        ('promotion', 'Promotion'),
        ('system', 'Système'),
    ]
    
    CHANNELS = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('both', 'SMS + Email'),
        ('push', 'Push Notification'),
    ]
    
    STATUS = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('delivered', 'Livré'),
        ('failed', 'Échec'),
        ('read', 'Lu'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNELS, default='email')
    
    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    
    # Delivery tracking
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Provider tracking
    sms_message_id = models.CharField(max_length=255, blank=True, null=True)
    email_message_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error):
        self.status = 'failed'
        self.error_message = error
        self.save()


class UserSession(models.Model):
    """Gestion des sessions utilisateur pour sécurité"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    
    # Session info
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.CharField(max_length=255, blank=True, null=True)
    
    # Location (if available)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_country = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_trusted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key', 'is_active']),
        ]
    
    def __str__(self):
        return f"Session {self.session_key[:8]}... - {self.user.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def end_session(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()


class OAuthToken(models.Model):
    """Stockage des tokens OAuth"""
    PROVIDERS = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oauth_tokens')
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    
    # OAuth credentials
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    id_token = models.TextField(blank=True, null=True)
    
    # Token info
    token_type = models.CharField(max_length=50, default='Bearer')
    scope = models.TextField(blank=True, null=True)
    
    # Expiration
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Provider user info
    provider_user_id = models.CharField(max_length=255)
    provider_email = models.EmailField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.provider} - {self.user.username}"
    
    def is_expired(self):
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class SecurityLog(models.Model):
    """Journal de sécurité pour audit"""
    EVENT_TYPES = [
        ('login_success', 'Connexion réussie'),
        ('login_failed', 'Échec de connexion'),
        ('login_otp', 'Connexion OTP'),
        ('logout', 'Déconnexion'),
        ('password_change', 'Changement de mot de passe'),
        ('account_locked', 'Compte verrouillé'),
        ('suspicious_activity', 'Activité suspecte'),
        ('oauth_connect', 'Connexion OAuth'),
        ('oauth_disconnect', 'Déconnexion OAuth'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs', blank=True, null=True)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    # Request info
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Additional data
    details = models.JSONField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user.username if self.user else 'Anonymous'}"

