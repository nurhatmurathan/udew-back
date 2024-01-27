from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Profile


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if value.startswith('+'):
            return value[1:]

        return value