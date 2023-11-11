import openai
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from api.serializers import UserPostSerializer

from .serializers import GPTChatSerializer

client = openai.OpenAI()


class GPTChatAPIView(APIView):
    def post(self, request):
        try:
            serializer = GPTChatSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user_message = serializer.data.get('message')

            prompt = "Give me an answer only on a scale of 10, like {'score': '4'}. " \
                     "Help me evaluate the answer to the question “At what stage is your startup currently at ?”. " \
                     "Answer: "

            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt + user_message}
                ]
            )

            response_message = response.choices[0].message.content
            return Response(response_message, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response(data={'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer
