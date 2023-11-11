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
            data_set = self._get_request_data()
            serialized_data = self._serialize_requested_data(data_set)

            gpt_response_list = []
            for question in serialized_data:

                request_message = self._get_prompt_text(question)

                response = client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": request_message}
                    ]
                )

                gpt_response_list.append(response.choices[0].message.content)

            return Response(data=gpt_response_list, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response(data={'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_prompt_text(self, question):
        return "Give me feedback(on words) for this answer. " \
                f"Question: {question['question']} " \
                f"Answer: {question['answer']}"

    def _serialize_requested_data(self, question_set):
        serializer = GPTChatSerializer(data=question_set, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    def _get_request_data(self):
        return self.request.data


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer
