"""
Signaux Django pour l'authentification avancée
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth import user_logged_in, user_login_failed, user_logged_out
from django.utils import timezone

from .models import UserProfile, SecurityLog
from .services import security_service


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement le profil utilisateur"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil utilisateur"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log la connexion réussie"""
    security_service.log_security_event(
        user, 'login_success', request,
        {'method': getattr(user.profile, 'preferred_auth_method', 'unknown')}
    )
    
    # Reset des tentatives échouées
    if hasattr(user, 'profile'):
        user.profile.reset_failed_attempts()


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log l'échec de connexion"""
    username = credentials.get('username', 'unknown')
    
    # Chercher l'utilisateur
    try:
        user = User.objects.get(username=username)
        # Incrémenter les tentatives échouées
        user.profile.failed_login_attempts += 1
        user.profile.last_failed_login = timezone.now()
        
        # Verrouiller le compte après 5 échecs
        if user.profile.failed_login_attempts >= 5:
            user.profile.lock_account(minutes=30)
        
        user.profile.save()
        
        security_service.log_security_event(
            user, 'login_failed', request,
            {'reason': 'invalid_credentials', 'attempts': user.profile.failed_login_attempts}
        )
    except User.DoesNotExist:
        security_service.log_security_event(
            None, 'login_failed', request,
            {'reason': 'user_not_found', 'username': username}
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log la déconnexion"""
    if user:
        security_service.log_security_event(user, 'logout', request)
