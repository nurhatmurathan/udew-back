from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound

from api.serializers.user import (
    UserCreateSerializer,
    UserUpdateSerializer,
    UserPasswordEditSerializer,
    UserSerializer
)


class UserCreateAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def post(self, request):
        try:
            data = request.data
            profile = self._pop_profile_from_data(data)


        except Exception as exception:
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


    def _pop_profile_from_data(self, data):
        if 'profile' not in data:
            raise NotFound("'profile' information is required.")




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