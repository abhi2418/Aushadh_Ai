from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework import routers
from users import views
router = routers.SimpleRouter()
from .views import (
    AuthUserRegistrationView,
    AuthUserLoginView,
    AuthUserListView,
    AuthVerifyPhone,
    AuthUpdatePassword,
    AuthLogoutView

)

urlpatterns = [
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('register', AuthUserRegistrationView.as_view(), name='register'),
    path('login', AuthUserLoginView.as_view(), name='login'),
    path('logout', AuthLogoutView.as_view(), name='logout'),
    path('users', AuthUserListView.as_view(), name='users'),
    path('send_sms_code/',views.send_sms_code),
    path('verify_register_number/<str:sms_code>',AuthVerifyPhone.as_view(),name='verify_register_number'),
    path('send_otp_reset/',AuthUpdatePassword.as_view(),name='send-otp'),
    path('send_otp_reset/<str:sms_code>',AuthUpdatePassword.as_view(),name='reset-otp'),
    
    
]

#pbkdf2_sha256$320000$5pWxbzmlzSzLLFGwpLtNfP$dubKBclOolFmqE/DcP3l9/Chf3tO8oe2h4FFIxDtNus=