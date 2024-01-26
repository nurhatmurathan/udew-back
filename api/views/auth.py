from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.serializers.auth import *


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserPasswordEditAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordEditSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
