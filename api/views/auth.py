import uuid

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from django.core.mail import send_mail
from django.conf import settings
from api.serializers.auth import UserCreateSerializer
from api.models import Profile, Token


class UserAPIView(APIView):
    def post(self, request):
        try:
            user_data = request.data
            serializer, user = self._validate_and_create_user(user_data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exception:
            return Response({"message": str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _validate_and_create_user(self, data):
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        return serializer, serializer.save()

    def _generate_token_for_user_email_confirmation(self, user):
        token = default_token_generator.make_token(user)
        user.email_confirm_token = token
        user.save()


class EmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            profile = self._get_user_profile(user)

            token = self._generate_token(profile)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            self._send_confirmation_email(user.email, uid, token.token)
            return Response({'message': 'Confirmation link sent to the email'}, status=status.HTTP_201_CREATED)
        except Exception as exception:
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_user_profile(self, user):
        try:
            profile = Profile.objects.get(user_id=user.id)
            return profile
        except Profile.DoesNotExist:
            return Profile.objects.create(user=user)

    def _generate_token(self, profile):
        if profile.confirmation_token and not profile.confirmation_token.is_expired():
            return profile.confirmation_token

        if profile.confirmation_token:
            profile.confirmation_token.delete()

        token = self._generate_unique_token()
        profile.confirmation_token = token
        profile.save()

        return token

    def _generate_unique_token(self):
        token = str(uuid.uuid4())
        while Token.objects.filter(token=token).exists():
            token = str(uuid.uuid4())

        return Token.objects.create(token=token)

    def _send_confirmation_email(self, email, uid, token):
        confirm_link = f'http://http://127.0.0.1:8000/confirm-email/?uid={uid}&token={token}'

        send_mail(
            'Confirm Your Account',
            f'Please click the following link to confirm your account: {confirm_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
