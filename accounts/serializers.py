from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'display_name', 'role', 
                  'national_id_number', 'fayda_fin', 'is_active', 'avatar')
        read_only_fields = ('role', 'is_active')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'display_name', 
                  'national_id_number', 'fayda_fin', 'role')
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'phone', 'national_id_number')
    
    def update(self, instance, validated_data):
        # Store requested changes in pending fields
        instance.pending_display_name = validated_data.get('display_name', instance.display_name)
        instance.pending_phone = validated_data.get('phone', instance.phone)
        instance.pending_national_id = validated_data.get('national_id_number', instance.national_id_number)
        instance.save()
        return instance