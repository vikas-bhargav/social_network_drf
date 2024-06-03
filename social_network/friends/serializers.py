"""This module provides serializers for Friends app"""
from rest_framework import serializers
from .models import User, FriendRequest


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, data):
        data["username"] = data["email"]
        user = User.objects.create_user(**data)
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    """Serializer for the FriendRequest model"""
    from_user_name = serializers.CharField(source='from_user.get_full_name', read_only=True)
    to_user_name = serializers.CharField(source='to_user.get_full_name', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'from_user_name', 'to_user_name','status',]

