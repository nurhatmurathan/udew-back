from django.contrib.auth.models import User
from rest_framework import serializers


class GPTChatSerializer(serializers.Serializer):
    question = serializers.CharField(allow_null=False, min_length=10)
    answer = serializers.CharField(allow_null=False, min_length=2)


class UserPostSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

