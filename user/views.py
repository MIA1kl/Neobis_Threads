from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomUser, OTP
from .serializers import (
    CustomUserSerializer,
    UserLoginSerializer,
    ResetPasswordSerializer,
    ForgotPasswordSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    OTPVerificationSerializer
)
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import authenticate





class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)

        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
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
            OTP.objects.filter(user=user).delete()
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
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user.is_private = user.is_private
        return user


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user.is_private = user.is_private
        return user
