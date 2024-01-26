from api.serializers.gpt import UserPostSerializer
from rest_framework import generics
from django.contrib.auth.models import User


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer