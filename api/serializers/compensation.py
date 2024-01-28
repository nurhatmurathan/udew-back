from rest_framework import serializers

from api.models import ApplicationCompensation


class ApplicationCompensationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationCompensation
        fields = ["id", "statement", "iin", "policy_number", "medical_documents", "status"]

    def create(self, validated_data):
        user = self.context['request'].user
        return ApplicationCompensation.objects.create(user=user, **validated_data)
