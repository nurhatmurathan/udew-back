from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics

from api.serializers import UserPostSerializer


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer

