from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'department', 'role',
            'is_anonymous', 'anon_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'anon_id', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        if obj.is_anonymous:
            return obj.anon_id
        return obj.name
    
    def get_email(self, obj):
        if obj.is_anonymous:
            return None
        return obj.email

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role', 'department']

    def create(self, validated_data):
        pwd = validated_data.pop('password')
        email = validated_data.get('email')
        # Set username as email
        validated_data['username'] = email
        user = User.objects.create(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data
