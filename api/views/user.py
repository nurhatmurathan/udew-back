import requests
import random

from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction

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
    UserSerializer,
    ProfileCreateSerializer
)


class UserCreateAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    @transaction.atomic
    def post(self, request):
        try:
            user_data = request.data

            user, user_serializer = self._user_serializer(user_data)
            data_from_government_about_user = self._get_data_from_government_about_user()

            profile_data = self._data_mapping(data_from_government_about_user)
            profile, profile_serializer = self._profile_serializer(profile_data, user)

            response_data = {
                **user_serializer.data,
                'profile': profile_serializer.data
            }
            return Response(data=response_data, status=status.HTTP_200_OK)
        except Exception as exception:
            transaction.set_rollback(True)
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _profile_serializer(self, data, user):
        serializer = ProfileCreateSerializer(instance=user.profile, data=data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        return instance, serializer

    def _data_mapping(self, source):
        return {
            'charges': source['charges'],
            'region': source['region'],
            'gender':  source['sex'],
            'smoker': source['smoker'],
            'children': source['children'],
            'age': source['age'],
            'body_mass_index': source['bmi'],
            'iin': source['iin']
        }

    def _user_serializer(self, data):
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        return instance, serializer


    def _get_data_from_government_about_user(self):
        headers = self._get_headers()

        url = settings.MINISTRY_OF_HEALTH_DATASET_URL
        dataset = self._make_request(url, headers=headers)

        random_iin = random.choice(dataset)
        url = f"{settings.MINISTRY_OF_HEALTH_DATASET_URL}/{random_iin.get('iin')}/"

        return self._make_request(url, headers=headers)

    def _get_headers(self):
        return {'Authorization': f'Bearer {settings.MINISTRY_OF_HEALTH_DATASET_API_KEY}'}

    def _make_request(self, url, headers):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()
        except requests.exceptions.HTTPError:
            return None
        except requests.exceptions.RequestException as exception:
            return Response({'message': 'Request failed', 'details': str(exception)},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)


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