from django.urls import path
from .views import AdminCreateUserView, CustomTokenObtainPairView, FinalLoginVerifyOTPView, MFASetupView, MFAVerifyView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [


    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/verify-otp/', FinalLoginVerifyOTPView.as_view(), name='login-verify-otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('auth/users/create/', AdminCreateUserView.as_view(), name='admin-create-user'),
    path('auth/me/', UserProfileView.as_view(), name='user-profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/users/create/', AdminCreateUserView.as_view(), name='admin-create-user'),

    # MFA
    path('auth/mfa/setup/', MFASetupView.as_view(), name='mfa-setup'),
    path('auth/mfa/verify/', MFAVerifyView.as_view(), name='mfa-verify'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]