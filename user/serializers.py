from rest_framework import serializers

from .models import CustomUser



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
