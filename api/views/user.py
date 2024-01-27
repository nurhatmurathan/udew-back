from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from api.serializers.user import (
    UserCreateSerializer,
    UserUpdateSerializer,
    UserPasswordEditSerializer,
    UserSerializer
)


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserUpdateSerializer
        else:
            return UserSerializer


class UserPasswordEditAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordEditSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user