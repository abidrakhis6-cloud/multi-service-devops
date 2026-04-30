"""
URLs pour l'authentification avancée
"""
from django.urls import path
from . import views

urlpatterns = [
    # ============ AUTHENTIFICATION CLASSIQUE ============
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============ AUTHENTIFICATION PAR TÉLÉPHONE ============
    path('phone/request-otp/', views.request_otp_view, name='request_otp'),
    path('phone/verify-otp/', views.verify_otp_view, name='verify_otp'),
    
    # ============ OAUTH ============
    path('oauth/login/', views.oauth_login_view, name='oauth_login'),
    
    # ============ PROFIL & SÉCURITÉ ============
    path('profile/', views.profile_view, name='profile'),
    path('profile/phone/', views.update_phone_view, name='update_phone'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('profile/auth-methods/', views.auth_methods_view, name='auth_methods'),
    
    # ============ MOT DE PASSE OUBLIÉ ============
    path('password/forgot/', views.forgot_password_view, name='forgot_password'),
    
    # ============ SESSIONS ============
    path('sessions/', views.UserSessionsView.as_view(), name='sessions'),
    path('sessions/<int:session_id>/terminate/', views.terminate_session_view, name='terminate_session'),
    path('sessions/terminate-all/', views.terminate_all_sessions_view, name='terminate_all_sessions'),
    
    # ============ SÉCURITÉ ============
    path('security/logs/', views.SecurityLogsView.as_view(), name='security_logs'),
    
    # ============ NOTIFICATIONS ============
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/', views.mark_notifications_read_view, name='mark_notifications_read'),
    path('notifications/unread-count/', views.unread_notifications_count_view, name='unread_notifications_count'),
]
