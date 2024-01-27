import requests
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.models import Profile
from api.serializers.chat import MessageSerializer
from udew.settings import OPENAI_CHAT_HEADERS
from api.chat_service import *


class MessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        profile = get_object_or_404(Profile, user=request.user)
        thread_id = profile.chat_thread_id

        chat = get_chat(thread_id)

        return Response(data=reversed(chat))

    def post(self, request, format=None):
        profile = get_object_or_404(Profile, user=request.user)
        thread_id = profile.chat_thread_id
        print(request.data)
        serializer = MessageSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
        print(serializer.data)
        response = requests.post(url, headers=OPENAI_CHAT_HEADERS, json=serializer.data)

        if response.ok:
            data = response.json()
            msg_id = data.get("id")
            if not msg_id:
                raise ValueError("message not is sent")
        else:
            response.raise_for_status()

        run_id = run_chat_assistant(thread_id)

        return Response(data={"run_id": run_id})


class ChatLastMessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, run_id, format=None):
        profile = get_object_or_404(Profile, user=request.user)
        thread_id = profile.chat_thread_id

        url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"

        response = requests.get(url, headers=OPENAI_CHAT_HEADERS)
        print(response.text)
        data = response.json()
        data_status = data.get("status")

        if data_status != "completed":
            return Response(data={"status": data_status})

        chat = get_chat(thread_id)

        return Response(data={"status": data_status,
                              "answer": chat[0]})
