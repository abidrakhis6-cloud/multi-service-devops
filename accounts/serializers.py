"""
Serializers pour l'API d'authentification et notifications
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, PhoneOTP, Notification, UserSession


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'phone_verified', 'google_id', 'facebook_id',
            'avatar_url', 'preferred_auth_method', 'created_at'
        ]
        read_only_fields = ['phone_verified', 'google_id', 'facebook_id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur avec profil"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Créer le profil avec le numéro de téléphone
        if phone_number:
            user.profile.phone_number = phone_number
            user.profile.save()
        
        return user


class PhoneAuthRequestSerializer(serializers.Serializer):
    """Serializer pour demander un code OTP"""
    phone_number = serializers.CharField(required=True, max_length=20)
    
    def validate_phone_number(self, value):
        # Nettoyer et valider le numéro
        value = value.replace(" ", "").replace("-", "").replace(".", "")
        if not value.startswith("+"):
            if value.startswith("0"):
                value = "+33" + value[1:]
            else:
                value = "+" + value
        
        # Validation basique
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Numéro de téléphone invalide.")
        
        return value


class PhoneAuthVerifySerializer(serializers.Serializer):
    """Serializer pour vérifier le code OTP"""
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Le code doit contenir uniquement des chiffres.")
        return value


class PhoneLoginSerializer(serializers.Serializer):
    """Serializer pour connexion par téléphone"""
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)


class OAuthLoginSerializer(serializers.Serializer):
    """Serializer pour connexion OAuth"""
    provider = serializers.ChoiceField(choices=['google', 'facebook'])
    access_token = serializers.CharField(required=True, help_text="Token d'accès OAuth")
    id_token = serializers.CharField(required=False, allow_blank=True, help_text="ID Token (pour Google)")


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'channel', 'channel_display',
            'title', 'message', 'status', 'status_display', 'sent_at', 'delivered_at', 
            'read_at', 'created_at'
        ]
        read_only_fields = fields


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer pour marquer une notification comme lue"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs des notifications à marquer comme lues (vide = toutes)"
    )


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions utilisateur"""
    is_current = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_key', 'ip_address', 'device_info', 'location_city', 
            'location_country', 'is_active', 'is_trusted', 'created_at', 
            'last_activity', 'is_current'
        ]
        read_only_fields = fields
    
    def get_is_current(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'session'):
            return obj.session_key == request.session.session_key
        return False


class SecurityLogSerializer(serializers.ModelSerializer):
    """Serializer pour le journal de sécurité"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = UserSession  # Remplacer par SecurityLog
        fields = ['id', 'event_type', 'event_type_display', 'ip_address', 'created_at', 'details']
        read_only_fields = fields


class ResendOTPSerializer(serializers.Serializer):
    """Serializer pour renvoyer un code OTP"""
    phone_number = serializers.CharField(required=True)


class UpdatePhoneSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le numéro de téléphone"""
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer pour mot de passe oublié"""
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer pour réinitialiser le mot de passe"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs
