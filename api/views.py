import openai
import requests
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
            for count_of_question, question in enumerate(serialized_data, start=1):
                request_message = self._get_prompt_text(question)
                response_content = self._get_gpt_response_content(request_message)

                gpt_response_list.append({
                    'number': count_of_question,
                    'content': response_content
                })
                count_of_question += 1

            return Response(data=gpt_response_list, status=status.HTTP_200_OK)
        except TimeoutError as timeout_error:
            return Response(data={'message': str(timeout_error)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as exception:
            return Response(data={'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _get_gpt_response_content(self, request_message):
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request_message}
                ],
                timeout=10
            )
            return response.choices[0].message.content
        except requests.exceptions.Timeout:
            raise TimeoutError("The request to OpenAI API timed out.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to OpenAI API: {str(e)}")

    def _get_prompt_text(self, question):
        return "Give me feedback(on words) for this answer of given question. " \
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
