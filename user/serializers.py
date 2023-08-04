from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, OTP
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import timedelta


class CustomUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'password', 'confirm_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        min_length = 8
        if len(value) < min_length:
            raise serializers.ValidationError(f'Password must be at least {min_length} characters long.')

        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one digit.')

        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError('Password must contain at least one letter.')

        if not any(char.isupper() for char in value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')

        return value

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


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_otp(self, value):
        try:
            otp_obj = OTP.objects.get(otp=value)
            if otp_obj.is_expired:
                raise serializers.ValidationError("OTP has expired.")
            self.user = otp_obj.user
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match!')

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    is_private = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name', 'username', 'profile_picture',  'bio', 'link', 'is_private')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    is_private = serializers.BooleanField()

    class Meta:
        model = CustomUser
        fields = ('name', 'username', 'bio', 'profile_picture', 'link', 'is_private')



