from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'department', 'role',
            'is_anonymous', 'anon_id', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'anon_id', 'created_at', 'updated_at']

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role', 'department']

    def create(self, validated_data):
        pwd = validated_data.pop('password')
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
