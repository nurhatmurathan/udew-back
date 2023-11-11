from rest_framework import serializers


class GPTChatSerializer(serializers.Serializer):
    message = serializers.CharField(allow_null=False, min_length=5)
