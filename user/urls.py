from django.urls import path, include
from .views import (
    UserRegistrationView,
    UserLoginView,
    ForgotPasswordView,
    ResetPasswordView,
    UserProfileDetailView,
    UserProfileUpdateView,
    VerifyOTPView, 
    UserLogoutView,
    UserContactViewSet,
    ConfirmSubscriptionView,
    UserProfilePictureUploadView,
    UserSearchView,
    FollowRequestView,
)
from rest_framework import routers

users_router = routers.DefaultRouter()
users_router.register(r'followers', UserContactViewSet, basename='followers')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='update-user-profile'),
    path('profile/avatar/', UserProfilePictureUploadView.as_view(), name='upload-avatar'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'), 
    path('verify-email/', VerifyOTPView.as_view(), name='verify_otp'), 
    path('confirm-subscription/<int:user_from_id>/', ConfirmSubscriptionView.as_view(), name='confirm-subscription'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('', include(users_router.urls)),
    path('user/search/', UserSearchView.as_view(), name='user-search'),
    path('follow/<int:user_id>/', FollowRequestView.as_view(), name='follow-request'),
    path('follower-requests/', FollowerRequestsView.as_view(), name='follower-requests'),
    path('follower-requests/<int:request_id>/', FollowerRequestsView.as_view(), name='accept-follower-request'),
]
