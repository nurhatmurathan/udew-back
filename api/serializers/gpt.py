from rest_framework import serializers


class GPTChatSerializer(serializers.Serializer):
    question = serializers.CharField(allow_null=False)
    answer = serializers.CharField(allow_null=False)

