from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    ForgotPasswordView,
    ResetPasswordView,
    UserProfileDetailView,
    UserProfileUpdateView,
    VerifyOTPView, 
    UserLogoutView
)


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='update-user-profile'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),  # New OTP verification endpoint

]

