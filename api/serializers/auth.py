from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Profile


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user)

        return user
