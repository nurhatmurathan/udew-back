import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone

from api.models import Profile, Token


class SendEmailAPIView(APIView):
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
        confirm_link = f'{settings.EMAIL_CONFIRMATION_REDIRECT_URL}/?uid={uid}&token={token}'
        email_content = render_to_string('confirmation_email.html', {'confirm_link': confirm_link})

        send_mail(
            'Confirm Your Account',
            '',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=email_content
        )


class ConfirmEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            uid, token = self._get_uid_and_token_from_query_params(request)

            uid = urlsafe_base64_decode(uid).decode()
            profile = self._get_user_profile(uid)

            self._check_token_validation(profile, token)
            self._update_profile_confirmation(profile)

            return Response({'message': 'Email successfully confirmed.'}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_uid_and_token_from_query_params(self, request):
        uid = request.query_params.get('uid', '')
        token = request.query_params.get('token', '')

        if not uid or not token:
            raise ValueError('uid and token are required in query parameters.')

        return uid, token

    def _get_user_profile(self, uid):
        try:
            user = User.objects.get(id=uid)
            return Profile.objects.get(user_id=user.id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise NotFound("User not found. Invalid token or user ID.")

    def _check_token_validation(self, profile, str_token):
        try:
            token = Token.objects.get(token=str_token)

            if not profile.confirmation_token:
                raise NotFound("User didn't generate token.")

            if token.is_expired():
                raise ValidationError("Token is expired.")

            if profile.confirmation_token.token != token.token:
                raise ValidationError("Your token doesn't match the user's token.")

        except Token.DoesNotExist:
            raise NotFound("Token not found.")

    def _update_profile_confirmation(self, profile):
        profile.is_email_confirmed = True
        profile.email_confirm_date = timezone.now()
        profile.save()

        if profile.confirmation_token:
            profile.confirmation_token.delete()

# class SendCodeAPIView(APIView):



