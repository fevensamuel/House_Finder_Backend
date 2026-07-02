# accounts/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'phone', 'display_name', 'role',
            'fayda_fin', 'is_active', 'avatar',
            'id_front', 'id_back',
            'cbe_bank_account', 'telebirr_phone', 'cbe_birr_phone',
            'is_profile_complete'
        )
        read_only_fields = ('role', 'is_active')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'display_name', 'fayda_fin', 'role')

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'display_name', 'phone', 'fayda_fin',
            'cbe_bank_account', 'telebirr_phone', 'cbe_birr_phone',
            'role'  # ✅ allow role update directly
        )