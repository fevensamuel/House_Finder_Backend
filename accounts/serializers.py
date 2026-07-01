# accounts/serializers.py
from rest_framework import serializers
from .models import User

# accounts/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'display_name', 'role', 'fayda_fin',
            'cbe_bank_account', 'telebirr_phone', 'cbe_birr_phone',
            'id_front', 'id_back', 'is_profile_complete',
            'avatar', 'is_active',
        ]
        read_only_fields = ['id']

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
        fields = ('display_name', 'phone', 'fayda_fin',
                  'cbe_bank_account', 'telebirr_phone', 'cbe_birr_phone')

    def update(self, instance, validated_data):
        instance.pending_display_name = validated_data.get('display_name', instance.display_name)
        instance.pending_phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance