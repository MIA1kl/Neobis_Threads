from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, OTP
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import timedelta


def validate_password(value):
    requirements = [
        (len(value) >= 6, 'Password must be at least 6 characters long.'),
        (len(value) <= 14, 'Password must be at most 14 characters long.'),
        (any(c.isdigit() for c in value), 'Password must contain at least one digit.'),
        (any(c.isalpha() for c in value), 'Password must contain at least one letter.'),
        (any(c.isupper() for c in value), 'Password must contain at least one uppercase letter.'),
        (any(not c.isalnum() for c in value), 'Password must contain at least one special character.')
    ]

    for condition, error_msg in requirements:
        if not condition:
            raise serializers.ValidationError(error_msg)
    return value


class CustomUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        return validate_password(value)


    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match!')

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        confirm_password = validated_data.pop('confirm_password')

        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    remember_me = serializers.BooleanField(default=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError('Invalid email or password.')

        refresh = RefreshToken.for_user(user)

        if data.get('remember_me'):
            refresh.access_token.set_exp(lifetime=timedelta(days=7))

        data['tokens'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        return value

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4)
    def validate_otp(self, value):
        try:
            otp_obj = OTP.objects.get(otp=value)
            if otp_obj.is_expired:
                raise serializers.ValidationError("OTP has expired.")
            self.user = otp_obj.user
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match!')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        data['user'] = user
        return data

    def validate_password(self, value):
        return validate_password(value)

    def create(self, validated_data):
        user = validated_data['user']
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    is_private = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'name', 'profile_picture',  'bio', 'link', 'is_private')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    is_private = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'bio', 'profile_picture', 'link', 'is_private')



