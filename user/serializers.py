from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, OTP, FollowingSystem
from thread.serializers import LikedUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import requests
from django.db.models import Q

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
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')


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
    otp = serializers.CharField(max_length=4)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        otp = data.get('otp')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        try:
            otp_obj = OTP.objects.get(otp=otp)
            if otp_obj.is_expired:
                raise serializers.ValidationError("OTP has expired.")
            data['user'] = otp_obj.user
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match!')

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
    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'name', 'profile_picture', 'bio', 'link', 'is_private', 'following', 'followers', 'followers_count')

    def get_followers_count(self, obj):
        # Получение количества подписчиков
        return obj.followers.count()

    def get_followers(self, obj):
        # Получение подписчиков, где пользователь 'obj' находится в rel_to_set и is_approved=True
        followers = FollowingSystem.objects.filter(user_to=obj, is_approved=True).select_related('user_from')
        return LikedUserSerializer([follower.user_from for follower in followers], many=True).data

    def get_following(self, obj):
        # Получение подписок, где пользователь 'obj' находится в rel_from_set и is_approved=True
        following = FollowingSystem.objects.filter(user_from=obj, is_approved=True).select_related('user_to')
        return LikedUserSerializer([follow.user_to for follow in following], many=True).data


class UserProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'bio', 'link', 'is_private')
        
        
class UserProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('profile_picture',)

    def validate_profile_picture(self, value):
        try:
            response = requests.head(value)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise serializers.ValidationError(_("Invalid image URL or the image is not accessible."))

        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image'):
            raise serializers.ValidationError(_("The provided URL does not point to an image."))

        # Check file size (max 3MB)
        max_size = 3 * 1024 * 1024  
        if 'content-length' in response.headers and int(response.headers['content-length']) > max_size:
            raise serializers.ValidationError(_("Image size exceeds the maximum limit of 3MB."))

        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
        if content_type not in allowed_formats:
            raise serializers.ValidationError(_("Image format is not supported. Allowed formats: jpg, jpeg, png."))

        return value


class UserContactSerializer(serializers.ModelSerializer):
    action = serializers.CharField()

    class Meta:
        model = FollowingSystem
        fields = [
            'user_to',
            'action',
            'is_pending',
        ]


class UserFollowingSerializer(serializers.ModelSerializer):
    following = LikedUserSerializer(many=True, read_only=True)
    followers = LikedUserSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'following',
            'followers',
        ]


class UserSearchSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'name', 'profile_picture', 'bio', 'link', 'is_private', 'is_following',
                  'followers_count')

    def get_is_following(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FollowingSystem.objects.filter(
                Q(user_from=user, user_to=obj, is_approved=True) |
                Q(user_from=obj, user_to=user, is_approved=True)
            ).exists()
        return False

    def get_followers_count(self, obj):
        return obj.followers.count()
