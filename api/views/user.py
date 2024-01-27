from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from api.serializers.user import UserCreateSerializer, UserSerializer, UserPasswordEditSerializer


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserProfileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPasswordEditAPIView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordEditSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user