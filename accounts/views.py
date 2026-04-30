"""
API Views pour authentification avancée
- Authentification par téléphone (OTP)
- OAuth (Google, Facebook)
- Notifications (SMS, Email)
- Gestion de sécurité
"""
import requests
import logging
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.authtoken.models import Token

from .models import (
    UserProfile, PhoneOTP, Notification, UserSession, 
    OAuthToken, SecurityLog
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, PhoneAuthRequestSerializer,
    PhoneAuthVerifySerializer, PhoneLoginSerializer, OAuthLoginSerializer,
    NotificationSerializer, NotificationMarkReadSerializer, PasswordChangeSerializer,
    UserSessionSerializer, SecurityLogSerializer, ResendOTPSerializer,
    UpdatePhoneSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from .services import (
    notification_service, otp_service, sms_service, 
    security_service, email_service
)

logger = logging.getLogger(__name__)
User = get_user_model()


# ============ RATE LIMITING ============

class LoginRateThrottle(AnonRateThrottle):
    """Rate limiting pour les tentatives de connexion"""
    rate = '5/minute'


class OTPRateThrottle(AnonRateThrottle):
    """Rate limiting pour les demandes OTP"""
    rate = '3/minute'


class RegisterRateThrottle(AnonRateThrottle):
    """Rate limiting pour l'inscription"""
    rate = '3/hour'


# ============ AUTHENTIFICATION CLASSIQUE ============

class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegisterRateThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            # Créer la session
            self._create_session(request, user)
            
            # Logger
            security_service.log_security_event(
                user, 'login_success', request, {'method': 'registration'}
            )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Inscription réussie'
        }, status=status.HTTP_201_CREATED)
    
    def _create_session(self, request, user):
        """Créer une session utilisateur"""
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or 'api-session',
            ip_address=security_service._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    """Connexion avec email/username et mot de passe"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Veuillez fournir un nom d\'utilisateur et un mot de passe.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier le rate limiting
    client_ip = security_service._get_client_ip(request)
    if not security_service.check_rate_limit(client_ip, 'login', max_attempts=5, window=300):
        security_service.log_security_event(
            None, 'suspicious_activity', request,
            {'reason': 'rate_limit_exceeded', 'username': username}
        )
        return Response(
            {'error': 'Trop de tentatives. Veuillez réessayer dans 5 minutes.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Authentification
    user = authenticate(username=username, password=password)
    
    if user is None:
        # Logger l'échec
        security_service.log_security_event(
            None, 'login_failed', request,
            {'reason': 'invalid_credentials', 'username': username}
        )
        return Response(
            {'error': 'Identifiants invalides.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Vérifier si le compte est verrouillé
    if user.profile.is_account_locked():
        security_service.log_security_event(
            user, 'login_failed', request,
            {'reason': 'account_locked'}
        )
        return Response(
            {'error': f'Compte temporairement verrouillé jusqu\'à {user.profile.account_locked_until}'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Succès
    security_service.reset_rate_limit(client_ip, 'login')
    login(request, user)
    token, created = Token.objects.get_or_create(user=user)
    
    # Créer la session
    UserSession.objects.create(
        user=user,
        session_key=request.session.session_key or 'api-session',
        ip_address=client_ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        expires_at=timezone.now() + timezone.timedelta(days=30)
    )
    
    # Reset failed attempts
    user.profile.reset_failed_attempts()
    
    # Logger
    security_service.log_security_event(
        user, 'login_success', request, {'method': 'password'}
    )
    
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key,
        'message': 'Connexion réussie'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Déconnexion"""
    user = request.user
    
    # Terminer les sessions
    UserSession.objects.filter(
        user=user,
        is_active=True
    ).update(is_active=False, ended_at=timezone.now())
    
    # Supprimer le token
    Token.objects.filter(user=user).delete()
    
    # Logger
    security_service.log_security_event(user, 'logout', request)
    
    logout(request)
    
    return Response({'message': 'Déconnexion réussie'})


# ============ AUTHENTIFICATION PAR TÉLÉPHONE (OTP) ============

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([OTPRateThrottle])
def request_otp_view(request):
    """Demander un code OTP par SMS"""
    serializer = PhoneAuthRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    
    # Vérifier le rate limiting par numéro
    if not security_service.check_rate_limit(phone_number, 'otp_request', max_attempts=3, window=600):
        return Response(
            {'error': 'Trop de demandes. Veuillez réessayer dans 10 minutes.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Chercher ou créer l'utilisateur
    try:
        profile = UserProfile.objects.get(phone_number=phone_number)
        user = profile.user
    except UserProfile.DoesNotExist:
        # Créer un utilisateur temporaire
        username = f"phone_{phone_number.replace('+', '').replace(' ', '')}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f"{username}@temp.multiserve.com"}
        )
        user.profile.phone_number = phone_number
        user.profile.save()
    
    # Générer et envoyer l'OTP
    otp, message = otp_service.generate_and_send_otp(user, phone_number)
    
    if otp is None:
        return Response(
            {'error': message},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Logger
    security_service.log_security_event(
        user, 'login_otp', request,
        {'phone_number': phone_number, 'otp_sent': True}
    )
    
    return Response({
        'message': 'Code envoyé par SMS',
        'expires_in': 600,  # 10 minutes en secondes
        'phone_masked': f"{phone_number[:4]}****{phone_number[-2:]}"
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginRateThrottle])
def verify_otp_view(request):
    """Vérifier le code OTP et connecter l'utilisateur"""
    serializer = PhoneAuthVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp_code']
    
    # Vérifier le rate limiting
    if not security_service.check_rate_limit(phone_number, 'otp_verify', max_attempts=5, window=300):
        return Response(
            {'error': 'Trop de tentatives. Veuillez réessayer dans 5 minutes.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Chercher l'utilisateur
    try:
        profile = UserProfile.objects.get(phone_number=phone_number)
        user = profile.user
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Numéro de téléphone non trouvé.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier l'OTP
    success, message = otp_service.verify_otp(phone_number, otp_code, user)
    
    if not success:
        # Logger l'échec
        security_service.log_security_event(
            user, 'login_failed', request,
            {'reason': 'invalid_otp', 'phone_number': phone_number}
        )
        return Response(
            {'error': message},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Succès
    security_service.reset_rate_limit(phone_number, 'otp_verify')
    login(request, user)
    token, created = Token.objects.get_or_create(user=user)
    
    # Créer la session
    UserSession.objects.create(
        user=user,
        session_key=request.session.session_key or 'api-session',
        ip_address=security_service._get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        device_info=request.data.get('device_info'),
        expires_at=timezone.now() + timezone.timedelta(days=30)
    )
    
    # Mettre à jour la méthode de connexion préférée
    user.profile.preferred_auth_method = 'phone'
    user.profile.save()
    
    # Logger
    security_service.log_security_event(
        user, 'login_success', request,
        {'method': 'phone_otp', 'phone_number': phone_number}
    )
    
    # Envoyer notification
    notification_service.send_notification(
        user=user,
        notification_type='security_alert',
        title='Nouvelle connexion détectée',
        message=f'Connexion via téléphone ({phone_number})',
        channel='email'
    )
    
    return Response({
        'user': UserSerializer(user).data,
        'token': token.key,
        'message': 'Connexion réussie'
    })


# ============ OAUTH (GOOGLE & FACEBOOK) ============

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def oauth_login_view(request):
    """Connexion via OAuth (Google ou Facebook)"""
    serializer = OAuthLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    provider = serializer.validated_data['provider']
    access_token = serializer.validated_data['access_token']
    
    try:
        if provider == 'google':
            user_data = _verify_google_token(access_token)
        elif provider == 'facebook':
            user_data = _verify_facebook_token(access_token)
        else:
            return Response(
                {'error': 'Provider non supporté'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user_data:
            return Response(
                {'error': 'Token invalide ou expiré'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Chercher ou créer l'utilisateur
        user = _get_or_create_oauth_user(user_data, provider)
        
        # Mettre à jour le token OAuth
        OAuthToken.objects.update_or_create(
            user=user,
            provider=provider,
            defaults={
                'access_token': access_token,
                'provider_user_id': user_data['id'],
                'provider_email': user_data.get('email', ''),
            }
        )
        
        # Connexion
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        
        # Créer la session
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key or 'api-session',
            ip_address=security_service._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timezone.timedelta(days=30)
        )
        
        # Mettre à jour la méthode de connexion
        user.profile.preferred_auth_method = provider
        user.profile.save()
        
        # Logger
        security_service.log_security_event(
            user, 'login_success', request,
            {'method': f'oauth_{provider}', 'email': user_data.get('email')}
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': f'Connexion {provider} réussie'
        })
        
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        return Response(
            {'error': 'Erreur lors de la connexion OAuth'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _verify_google_token(access_token):
    """Vérifie le token Google et retourne les infos utilisateur"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'id': data.get('sub'),
                'email': data.get('email'),
                'name': data.get('name'),
                'picture': data.get('picture'),
                'verified_email': data.get('email_verified', False)
            }
        return None
    except Exception as e:
        logger.error(f"Google token verification error: {e}")
        return None


def _verify_facebook_token(access_token):
    """Vérifie le token Facebook et retourne les infos utilisateur"""
    try:
        # D'abord vérifier le token
        debug_response = requests.get(
            'https://graph.facebook.com/debug_token',
            params={
                'input_token': access_token,
                'access_token': f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
            }
        )
        
        if debug_response.status_code != 200:
            return None
        
        debug_data = debug_response.json().get('data', {})
        if not debug_data.get('is_valid'):
            return None
        
        # Récupérer les infos utilisateur
        user_response = requests.get(
            'https://graph.facebook.com/me',
            params={
                'access_token': access_token,
                'fields': 'id,name,email,picture'
            }
        )
        
        if user_response.status_code == 200:
            data = user_response.json()
            return {
                'id': data.get('id'),
                'email': data.get('email'),
                'name': data.get('name'),
                'picture': data.get('picture', {}).get('data', {}).get('url')
            }
        return None
    except Exception as e:
        logger.error(f"Facebook token verification error: {e}")
        return None


def _get_or_create_oauth_user(user_data, provider):
    """Récupère ou crée un utilisateur OAuth"""
    email = user_data.get('email')
    provider_id = user_data.get('id')
    
    with transaction.atomic():
        # Chercher par provider ID
        if provider == 'google':
            try:
                profile = UserProfile.objects.get(google_id=provider_id)
                return profile.user
            except UserProfile.DoesNotExist:
                pass
        elif provider == 'facebook':
            try:
                profile = UserProfile.objects.get(facebook_id=provider_id)
                return profile.user
            except UserProfile.DoesNotExist:
                pass
        
        # Chercher par email
        if email:
            try:
                user = User.objects.get(email=email)
                # Mettre à jour le provider ID
                if provider == 'google':
                    user.profile.google_id = provider_id
                elif provider == 'facebook':
                    user.profile.facebook_id = provider_id
                user.profile.save()
                return user
            except User.DoesNotExist:
                pass
        
        # Créer un nouvel utilisateur
        username = email.split('@')[0] if email else f"{provider}_{provider_id[:10]}"
        base_username = username
        counter = 1
        
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email or f"{provider}_{provider_id}@oauth.multiserve.com",
            first_name=user_data.get('name', '').split()[0] if user_data.get('name') else '',
            last_name=' '.join(user_data.get('name', '').split()[1:]) if user_data.get('name') else ''
        )
        
        # Mettre à jour le profil
        if provider == 'google':
            user.profile.google_id = provider_id
        elif provider == 'facebook':
            user.profile.facebook_id = provider_id
        
        user.profile.avatar_url = user_data.get('picture')
        user.profile.preferred_auth_method = provider
        user.profile.save()
        
        return user


# ============ NOTIFICATIONS ============

class NotificationListView(generics.ListAPIView):
    """Liste des notifications de l'utilisateur"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read_view(request):
    """Marquer des notifications comme lues"""
    serializer = NotificationMarkReadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    notification_ids = serializer.validated_data.get('notification_ids', [])
    
    if notification_ids:
        # Marquer spécifiques
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        )
    else:
        # Marquer toutes
        notifications = Notification.objects.filter(
            user=request.user,
            status__in=['sent', 'delivered']
        )
    
    count = 0
    for notification in notifications:
        notification.mark_as_read()
        count += 1
    
    return Response({
        'message': f'{count} notification(s) marquée(s) comme lue(s)'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_notifications_count_view(request):
    """Nombre de notifications non lues"""
    count = Notification.objects.filter(
        user=request.user,
        status__in=['sent', 'delivered']
    ).count()
    
    return Response({
        'unread_count': count
    })


# ============ GESTION DU PROFIL ============

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Récupérer ou modifier le profil"""
    user = request.user
    
    if request.method == 'GET':
        return Response(UserSerializer(user).data)
    
    # PUT - Mise à jour
    data = request.data
    
    # Mise à jour des champs User
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    
    user.save()
    
    # Mise à jour du profil
    profile = user.profile
    if 'avatar_url' in data:
        profile.avatar_url = data['avatar_url']
    
    profile.save()
    
    return Response(UserSerializer(user).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_phone_view(request):
    """Mettre à jour le numéro de téléphone avec vérification OTP"""
    serializer = UpdatePhoneSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp_code = serializer.validated_data['otp_code']
    
    # Vérifier l'OTP
    success, message = otp_service.verify_otp(phone_number, otp_code)
    
    if not success:
        return Response(
            {'error': message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mettre à jour le numéro
    request.user.profile.phone_number = phone_number
    request.user.profile.phone_verified = True
    request.user.profile.save()
    
    return Response({
        'message': 'Numéro de téléphone mis à jour avec succès',
        'phone_number': phone_number
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Changer le mot de passe"""
    serializer = PasswordChangeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Vérifier l'ancien mot de passe
    if not user.check_password(serializer.validated_data['old_password']):
        security_service.log_security_event(
            user, 'login_failed', request,
            {'reason': 'invalid_old_password'}
        )
        return Response(
            {'error': 'Ancien mot de passe incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Changer le mot de passe
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    # Logger
    security_service.log_security_event(user, 'password_change', request)
    
    # Notification
    notification_service.send_security_alert(
        user,
        'password_change',
        'Votre mot de passe a été changé',
        security_service._get_client_ip(request)
    )
    
    return Response({'message': 'Mot de passe changé avec succès'})


# ============ SÉCURITÉ & SESSIONS ============

class UserSessionsView(generics.ListAPIView):
    """Liste des sessions actives"""
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_session_view(request, session_id):
    """Terminer une session spécifique"""
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user,
            is_active=True
        )
        
        # Ne pas permettre de terminer la session courante via cette vue
        if session.session_key == request.session.session_key:
            return Response(
                {'error': 'Utilisez la déconnexion pour terminer cette session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.end_session()
        
        return Response({'message': 'Session terminée avec succès'})
        
    except UserSession.DoesNotExist:
        return Response(
            {'error': 'Session non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def terminate_all_sessions_view(request):
    """Terminer toutes les sessions sauf la courante"""
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).exclude(session_key=request.session.session_key or 'api-session')
    
    count = sessions.count()
    sessions.update(is_active=False, ended_at=timezone.now())
    
    return Response({
        'message': f'{count} session(s) terminée(s) avec succès'
    })


class SecurityLogsView(generics.ListAPIView):
    """Journal de sécurité"""
    serializer_class = SecurityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SecurityLog.objects.filter(user=self.request.user)[:50]


# ============ MOT DE PASSE OUBLIÉ ============

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([OTPRateThrottle])
def forgot_password_view(request):
    """Demander une réinitialisation de mot de passe"""
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    try:
        user = User.objects.get(email=email)
        
        # Générer un token de réinitialisation
        from django.contrib.auth.tokens import default_token_generator
        token = default_token_generator.make_token(user)
        
        # Envoyer l'email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}&uid={user.pk}"
        
        email_service.send_notification_email(
            to_email=email,
            notification_type='security_alert',
            title='Réinitialisation de votre mot de passe',
            message=f'Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {reset_url}',
            action_url=reset_url
        )
        
        return Response({
            'message': 'Un email de réinitialisation a été envoyé si l\'adresse existe'
        })
        
    except User.DoesNotExist:
        # Réponse identique pour ne pas révéler l'existence de l'email
        return Response({
            'message': 'Un email de réinitialisation a été envoyé si l\'adresse existe'
        })


# ============ UTILITAIRES ============

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_methods_view(request):
    """Récupérer les méthodes d'authentification disponibles"""
    user = request.user
    profile = user.profile
    
    return Response({
        'password': True,
        'phone': {
            'enabled': bool(profile.phone_number and profile.phone_verified),
            'phone_masked': f"{profile.phone_number[:4]}****{profile.phone_number[-2:]}" if profile.phone_number else None
        },
        'google': {
            'enabled': bool(profile.google_id),
            'connected': OAuthToken.objects.filter(user=user, provider='google').exists()
        },
        'facebook': {
            'enabled': bool(profile.facebook_id),
            'connected': OAuthToken.objects.filter(user=user, provider='facebook').exists()
        }
    })

