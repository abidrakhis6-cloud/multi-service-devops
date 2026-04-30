"""
Services de notification et authentification
- SMS via Twilio
- Email via SendGrid
- OAuth via Google/Facebook
"""

import os
import logging
from typing import Optional, Tuple
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

# Twilio pour SMS
try:
    from twilio.rest import Client as TwilioClient
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    TwilioClient = None
    TwilioRestException = Exception

# SendGrid pour Email
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    sendgrid = None

from .models import Notification, PhoneOTP, SecurityLog

logger = logging.getLogger(__name__)


class SMSService:
    """Service d'envoi de SMS via Twilio"""
    
    def __init__(self):
        self.client = None
        self.from_number = None
        
        # Initialiser Twilio si les credentials sont disponibles
        if TwilioClient and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = TwilioClient(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.from_number = settings.TWILIO_PHONE_NUMBER
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
    
    def is_configured(self) -> bool:
        """Vérifie si le service SMS est configuré"""
        return self.client is not None and self.from_number is not None
    
    def send_sms(self, to_number: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Envoie un SMS
        
        Args:
            to_number: Numéro de téléphone (format international)
            message: Contenu du message
            
        Returns:
            Tuple (success: bool, message_id: str or error_message)
        """
        if not self.is_configured():
            logger.warning("Twilio not configured. SMS not sent.")
            return False, "SMS service not configured"
        
        # Normaliser le numéro
        to_number = self._normalize_phone(to_number)
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message_obj.sid}")
            return True, message_obj.sid
            
        except TwilioRestException as e:
            logger.error(f"Twilio error: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            return False, str(e)
    
    def send_otp(self, to_number: str, otp_code: str) -> Tuple[bool, Optional[str]]:
        """Envoie un code OTP par SMS"""
        message = f"Votre code de vérification MultiServe est: {otp_code}. Valable 10 minutes."
        return self.send_sms(to_number, message)
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normalise le numéro de téléphone au format international"""
        phone = phone.replace(" ", "").replace("-", "").replace(".", "")
        if not phone.startswith("+"):
            # Par défaut, ajouter l'indicatif français si pas présent
            if phone.startswith("0"):
                phone = "+33" + phone[1:]
            else:
                phone = "+" + phone
        return phone


class EmailService:
    """Service d'envoi d'emails via SendGrid ou SMTP"""
    
    def __init__(self):
        self.sg_client = None
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@multiserve.com')
        
        # Initialiser SendGrid si disponible
        if sendgrid and settings.SENDGRID_API_KEY:
            try:
                self.sg_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                logger.info("SendGrid client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid: {e}")
    
    def is_sendgrid_configured(self) -> bool:
        return self.sg_client is not None
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet
            message: Contenu texte
            html_message: Contenu HTML (optionnel)
            
        Returns:
            Tuple (success: bool, message_id or error)
        """
        try:
            # Essayer SendGrid d'abord
            if self.is_sendgrid_configured() and html_message:
                return self._send_sendgrid(to_email, subject, html_message)
            
            # Sinon utiliser Django SMTP
            return self._send_django_email(to_email, subject, message, html_message)
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False, str(e)
    
    def _send_sendgrid(self, to_email: str, subject: str, html_content: str) -> Tuple[bool, Optional[str]]:
        """Envoi via SendGrid"""
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg_client.client.mail.send.post(request_body=message.get())
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent via SendGrid to {to_email}")
                return True, response.headers.get('X-Message-Id')
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False, f"SendGrid error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"SendGrid exception: {e}")
            return False, str(e)
    
    def _send_django_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Envoi via Django SMTP"""
        try:
            sent = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            if sent > 0:
                logger.info(f"Email sent via SMTP to {to_email}")
                return True, f"django-{timezone.now().timestamp()}"
            else:
                return False, "Email not sent"
                
        except Exception as e:
            logger.error(f"Django email error: {e}")
            return False, str(e)
    
    def send_notification_email(
        self, 
        to_email: str, 
        notification_type: str, 
        title: str, 
        message: str,
        action_url: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Envoie un email de notification formaté"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .button {{ display: inline-block; background: #2563eb; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px; margin-top: 20px; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    <p>Bonjour,</p>
                    <p>{message}</p>
                    {f'<a href="{action_url}" class="button">Voir les détails</a>' if action_url else ''}
                </div>
                <div class="footer">
                    <p>© 2026 MultiServe - Tous droits réservés</p>
                    <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, title, message, html_template)


class NotificationService:
    """Service central de notifications"""
    
    def __init__(self):
        self.sms_service = SMSService()
        self.email_service = EmailService()
    
    def send_notification(
        self, 
        user, 
        notification_type: str, 
        title: str, 
        message: str,
        channel: str = 'email',
        action_url: Optional[str] = None,
        send_sms: bool = False,
        send_email: bool = True
    ) -> Notification:
        """
        Crée et envoie une notification
        
        Args:
            user: L'utilisateur destinataire
            notification_type: Type de notification
            title: Titre
            message: Message
            channel: Canal ('sms', 'email', 'both')
            action_url: URL d'action (optionnel)
            send_sms: Forcer l'envoi SMS
            send_email: Forcer l'envoi email
            
        Returns:
            L'objet Notification créé
        """
        from .models import Notification
        
        # Créer l'enregistrement
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            channel=channel,
            title=title,
            message=message
        )
        
        # Envoyer selon le canal
        success = False
        
        if channel in ['sms', 'both'] or send_sms:
            if user.profile and user.profile.phone_number and user.profile.phone_verified:
                sms_success, sms_id = self.sms_service.send_sms(
                    user.profile.phone_number,
                    f"{title}: {message}"
                )
                if sms_success:
                    notification.sms_message_id = sms_id
                    success = True
        
        if channel in ['email', 'both'] or send_email:
            if user.email:
                email_success, email_id = self.email_service.send_notification_email(
                    user.email,
                    notification_type,
                    title,
                    message,
                    action_url
                )
                if email_success:
                    notification.email_message_id = email_id
                    notification.mark_as_sent()
                    success = True
        
        if not success:
            notification.mark_as_failed("Aucun canal de notification disponible")
        
        return notification
    
    def send_new_message_notification(self, user, sender_name: str, message_preview: str):
        """Notification de nouveau message"""
        return self.send_notification(
            user=user,
            notification_type='new_message',
            title=f"Nouveau message de {sender_name}",
            message=f"Vous avez reçu un nouveau message: {message_preview[:100]}...",
            channel='both'
        )
    
    def send_security_alert(self, user, event_type: str, details: str, ip_address: str = None):
        """Alerte de sécurité"""
        return self.send_notification(
            user=user,
            notification_type='security_alert',
            title="Alerte de sécurité - MultiServe",
            message=f"{details}\n\nIP: {ip_address or 'Inconnue'}",
            channel='both'
        )
    
    def send_order_update(self, user, order_id: str, status: str):
        """Mise à jour de commande"""
        return self.send_notification(
            user=user,
            notification_type='order_update',
            title=f"Mise à jour de votre commande #{order_id}",
            message=f"Votre commande est maintenant: {status}",
            channel='email'
        )


class OTPService:
    """Service de gestion des codes OTP"""
    
    @staticmethod
    def generate_and_send_otp(user, phone_number: str) -> Tuple[Optional[PhoneOTP], str]:
        """
        Génère et envoie un code OTP
        
        Returns:
            Tuple (PhoneOTP object, message)
        """
        # Nettoyer les anciens codes non utilisés pour ce numéro
        PhoneOTP.objects.filter(
            phone_number=phone_number,
            is_used=False
        ).update(is_used=True)
        
        # Créer nouveau code
        otp = PhoneOTP.objects.create(
            user=user,
            phone_number=phone_number
        )
        
        # Envoyer par SMS
        sms_service = SMSService()
        if sms_service.is_configured():
            success, message_id = sms_service.send_otp(phone_number, otp.otp_code)
            if success:
                return otp, "Code envoyé par SMS"
            else:
                otp.delete()
                return None, f"Erreur d'envoi SMS: {message_id}"
        else:
            # Mode développement - retourner le code sans l'envoyer
            logger.warning(f"SMS not configured. OTP for {phone_number}: {otp.otp_code}")
            return otp, f"Mode développement - Code: {otp.otp_code}"
    
    @staticmethod
    def verify_otp(phone_number: str, code: str, user=None) -> Tuple[bool, str]:
        """
        Vérifie un code OTP
        
        Returns:
            Tuple (success, message)
        """
        # Chercher le dernier code valide
        otp = PhoneOTP.objects.filter(
            phone_number=phone_number,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp:
            return False, "Aucun code actif trouvé"
        
        # Vérifier
        success, message = otp.verify(code)
        
        if success and user:
            # Marquer le numéro comme vérifié
            user.profile.phone_number = phone_number
            user.profile.phone_verified = True
            user.profile.save()
        
        return success, message


class SecurityService:
    """Service de sécurité et audit"""
    
    @staticmethod
    def log_security_event(user, event_type: str, request=None, details: dict = None):
        """Enregistre un événement de sécurité"""
        log_data = {
            'user': user,
            'event_type': event_type,
            'details': details or {}
        }
        
        if request:
            log_data['ip_address'] = SecurityService._get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        SecurityLog.objects.create(**log_data)
        logger.info(f"Security event: {event_type} - User: {user.username if user else 'Anonymous'}")
    
    @staticmethod
    def _get_client_ip(request) -> str:
        """Récupère l'IP client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
    
    @staticmethod
    def check_rate_limit(identifier: str, action: str, max_attempts: int = 5, window: int = 300) -> bool:
        """
        Vérifie la limite de tentatives
        
        Args:
            identifier: Identifiant (IP, username, phone)
            action: Type d'action
            max_attempts: Nombre max de tentatives
            window: Fenêtre de temps en secondes
            
        Returns:
            True si autorisé, False sinon
        """
        from django.core.cache import cache
        
        cache_key = f"rate_limit:{action}:{identifier}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= max_attempts:
            return False
        
        cache.set(cache_key, attempts + 1, window)
        return True
    
    @staticmethod
    def reset_rate_limit(identifier: str, action: str):
        """Réinitialise le compteur de tentatives"""
        from django.core.cache import cache
        cache_key = f"rate_limit:{action}:{identifier}"
        cache.delete(cache_key)


# Instance singleton pour utilisation facile
notification_service = NotificationService()
otp_service = OTPService()
sms_service = SMSService()
email_service = EmailService()
security_service = SecurityService()
