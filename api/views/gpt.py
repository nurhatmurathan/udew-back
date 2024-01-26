import openai
import requests
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from api.serializers.gpt import UserPostSerializer
from api.serializers.gpt import GPTChatSerializer

client = openai.OpenAI()


class GPTChatAPIView(APIView):
    def post(self, request):
        try:
            data_set = self._get_request_data()
            serialized_data = self._serialize_requested_data(data_set)

            questions = self._collect_questions_into_str(serialized_data)

            prompt_text = self._get_prompt_text(questions)
            gpt_response = self._get_gpt_response_content(prompt_text)

            return Response(data={"score": gpt_response}, status=status.HTTP_200_OK)
        except TimeoutError as timeout_error:
            return Response(data={'message': str(timeout_error)}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as exception:
            return Response(data={'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)

    def _collect_questions_into_str(self, serialized_data):
        return "\n".join(
                [f"Question: {item['question']}\nAnswer: {item['answer']}" for item in serialized_data])

    def _get_gpt_response_content(self, request_message):
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request_message}
                ],
                timeout=20
            )
            return response.choices[0].message.content
        except requests.exceptions.Timeout:
            raise TimeoutError("The request to OpenAI API timed out.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error connecting to OpenAI API: {str(e)}")

    def _get_prompt_text(self, questions):
        return "Rate the startup based on the following answers to the questions:\n" \
               f"{questions}\n  Startup rating from 0 to 10.\n" \
               "Send me response, for example: 8 without words like 'Based on the answers provided, I would rate this "\
               "startup a', send only the number without words, how much you rated this startup."

    def _serialize_requested_data(self, question_set):
        serializer = GPTChatSerializer(data=question_set, many=True)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data

    def _get_request_data(self):
        return self.request.data


class UserCreateCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPostSerializer
