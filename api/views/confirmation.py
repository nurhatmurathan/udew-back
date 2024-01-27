import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Profile, Token, Code
from api.serializers.confirmation import PhoneNumberSerializer
from api.utils import generate_digit_code


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
#     def post(self, request):
#         try:
#             print("Step 1")
#             phone_number = self._phone_number_serializer(request.data)
#             print("Step 2")
#             code = self._generate_code()
#
#             print("Step 3")
#             self._send_whatsapp_message(phone_number, code.code)
#             print("Step 4")
#             return Response({'message': 'Confirmation link sent to your WhatsApp number.'}, status=status.HTTP_200_OK)
#         except Exception as exception:
#             return Response({'meesages': str(exception)}, status=status.HTTP_400_BAD_REQUEST)
#
#     def _phone_number_serializer(self, data):
#         serializer = PhoneNumberSerializer(data=data)
#         serializer.is_valid(raise_exception=True)
#
#         return serializer.validated_data['phone_number']
#
#     def _generate_code(self):
#         code = generate_digit_code()
#         while Code.objects.filter(code=code).exists():
#             code = generate_digit_code()
#
#         return Code.objects.create(code=code)
#
#     def _send_whatsapp_message(self, recipient, placeholder):
#         # connection = http.client.HTTPSConnection(settings.WHATSAPP_API_BASE_URL)
#         #
#         # print(placeholder, " ", recipient)
#         # print(connection)
#         # print(settings.WHATSAPP_MESSAGE_ID)
#         # print(settings.WHATSAPP_MESSAGE_API)
#         # print(settings.WHATSAPP_TEST_SENDER)
#         # print(settings.WHATSAPP_API_BASE_URL)
#         # print(settings.WHATSAPP_TEST_SENDER_URL)
#         #
#         # payload = json.dumps({
#         #     "messages": [
#         #         {
#         #             "from": settings.WHATSAPP_TEST_SENDER,
#         #             "to": recipient,
#         #             "messageId": settings.WHATSAPP_MESSAGE_ID,
#         #             "content": {
#         #                 "templateName": "welcome_messages",
#         #                 "templateData": {
#         #                     "body": {
#         #                         "placeholders": [placeholder]
#         #                     }
#         #                 },
#         #                 "language": "en"
#         #             }
#         #         }
#         #     ]
#         # })
#         # headers = {
#         #     'Authorization': f'App {settings.WHATSAPP_MESSAGE_API}',
#         #     'Content-Type': 'application/json',
#         #     'Accept': 'application/json'
#         # }
#         #
#         # connection.request("POST", settings.WHATSAPP_TEST_SENDER_URL, payload, headers)
#         # res = connection.getresponse()
#         # data = res.read()
#         # print(data.decode("utf-8"))
#
#         BASE_URL = "https://y3xle1.api.infobip.com"
#         API_KEY = "App e4f6cd18f0f72c13cbeb4fc59c592f6c-2a8404db-78c8-4ef6-ab40-23762e8e9ae5"
#
#         SENDER = "447860099299"
#         RECIPIENT = "77003929771"
#
#         print(recipient)
#         payload = {
#             "messages":
#                 [
#                     {
#                         "from": SENDER,
#                         "to": recipient,
#                         "content": {
#                             "templateName": "message_test",
#                             "templateData": {
#                                 "body": {
#                                     "placeholders": [placeholder]
#                                 }
#                             },
#                             "language": "en"
#                         }
#                     }
#                 ]
#         }
#
#         headers = {
#             'Authorization': API_KEY,
#             'Content-Type': 'application/json',
#             'Accept': 'application/json'
#         }
#
#         response = requests.post(BASE_URL + "/whatsapp/1/message/template", json=payload, headers=headers)
#
#         print(response.json())
