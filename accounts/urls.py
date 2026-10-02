from django.urls import path
from accounts import views

urlpatterns = [
    path('register', views.register, name='auth-register'),
    path('login', views.login, name='auth-login'),
    path('refresh-token', views.refresh_token, name='auth-refresh'),
    path('logout', views.logout, name='auth-logout'),
    # Forgot Password
    path('forgot-password/send-otp', views.forgot_password_send_otp, name='forgot-password-send-otp'),
    path('forgot-password/send-otp/', views.forgot_password_send_otp, name='forgot-password-send-otp-slash'),
    path('forgot-password/verify-and-reset', views.forgot_password_verify_and_reset, name='forgot-password-verify-and-reset'),
    path('forgot-password/verify-and-reset/', views.forgot_password_verify_and_reset, name='forgot-password-verify-and-reset-slash'),
]

