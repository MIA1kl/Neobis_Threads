from datetime import timedelta
from rest_framework import generics, viewsets, views
from rest_framework.response import Response
from rest_framework import status, filters
from cloudinary.uploader import upload
from .models import CustomUser
from .serializers import (
    CustomUserSerializer,
    UserLoginSerializer,
    ResetPasswordSerializer,
    ForgotPasswordSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    OTPVerificationSerializer,
    UserContactSerializer,
    UserFollowingSerializer,
    LogoutSerializer,
    UserProfilePictureSerializer,
    UserSearchSerializer
)
from .mixins import BaseUserProfileViewMixin
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP, FollowingSystem
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
import threading


class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            otp_code = OTP.generate_otp()
            user = serializer.save()
            OTP.objects.create(user=user, otp=otp_code)
            # Send the OTP to the user's email
            subject = 'Verify Email OTP'
            message = f'Your OTP is: {otp_code}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)
            timer = threading.Timer(120, self.delete_user, args=[user.id])
            timer.start()
            user.save()
        return Response({"message": "OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete_user(self, user_id):
        CustomUser.objects.filter(id=user_id, is_verified=False).delete()
        



class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')

        refresh = RefreshToken.for_user(user)

        if not SocialAccount.objects.filter(user=user).exists():
            if remember_me:
                refresh.access_token.set_exp(lifetime=timedelta(days=7))
        else:
            if remember_me:
                refresh.access_token.set_exp(lifetime=timedelta(days=7))

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
        

class UserLogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            otp_code = OTP.generate_otp()
            OTP.objects.filter(user=user).delete()
            OTP.objects.create(user=user, otp=otp_code)

            # Send the OTP to the user's email
            subject = 'Forgot Password OTP'
            message = f'Your OTP is: {otp_code}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            user.is_verified = True  # Set is_verified to True
            user.save() 
            return Response({"message": "OTP verification successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            password = serializer.validated_data['password']
            user.set_password(password)
            user.save()
            OTP.objects.filter(user=user).delete()  
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserProfileDetailView(BaseUserProfileViewMixin, generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer

    def get_pending_follow_requests(self, request, *args, **kwargs):
        user = self.request.user
        pending_follow_requests = FollowingSystem.objects.filter(user_to=user, is_approved=False)
        serializer = UserSearchSerializer(pending_follow_requests.values('user_from'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        if request.query_params.get('pending_follow_requests'):
            return self.get_pending_follow_requests(request, *args, **kwargs)

        return super().get(request, *args, **kwargs)


class UserProfileUpdateView(BaseUserProfileViewMixin, generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer



class UserProfilePictureUploadView(generics.GenericAPIView):
    serializer_class = UserProfilePictureSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UserProfilePictureSerializer(user, data=request.data)

        if serializer.is_valid():
            uploaded_file = upload(request.data['profile_picture'])
            user.profile_picture = uploaded_file['url']
            user.save()

            return Response({'message': 'Profile picture uploaded successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserContactViewSet(viewsets.ViewSet):
    serializer_class = UserContactSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'

    def create(self, request):
        serializer = UserContactSerializer(data=request.data)
        if serializer.is_valid():
            to_user = CustomUser.objects.get(id=serializer.data['user_to'])
            is_private = to_user.is_private

            if self.request.user != to_user:
                try:
                    if serializer.data['action'] == 'follow':
                        if is_private:
                            FollowingSystem.objects.create(user_from=self.request.user, user_to=to_user)
                            return Response({'status': 'request_sent'})
                        else:
                            FollowingSystem.objects.create(user_from=self.request.user, user_to=to_user,
                                                           is_approved=True)
                            return Response({'status': 'followed'})

                    if serializer.data['action'] == 'unfollow':
                        FollowingSystem.objects.filter(user_from=self.request.user, user_to=to_user).delete()
                        return Response({'status': 'unfollowed'})

                except:
                    return Response({'status': 'error'})
            else:
                return Response({'status': 'no_need_to_follow_yourself'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # authenticated user can search for any user's public info
    def retrieve(self, request, username=None):
        queryset = CustomUser.objects.all()
        user = get_object_or_404(queryset, username=username)
        serializer = UserFollowingSerializer(user)
        return Response(serializer.data)


class ConfirmSubscriptionView(generics.UpdateAPIView):
    serializer_class = UserContactSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_to = self.request.user
        user_from_id = kwargs.get('user_from_id')

        try:
            following = FollowingSystem.objects.get(user_from_id=user_from_id, user_to=user_to, is_approved=False)
            following.is_approved = True
            following.save()
            return Response({'status': 'approved'})
        except FollowingSystem.DoesNotExist:
            return Response({'status': 'not_found'}, status=status.HTTP_404_NOT_FOUND)


class UserSearchView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'name']

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = CustomUser.objects.filter(is_active=True, username__icontains=search_query)
        else:
            queryset = CustomUser.objects.filter(is_active=True)

        return queryset

