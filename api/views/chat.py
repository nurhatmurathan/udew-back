import requests
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.models import Profile, Message
from api.serializers.chat import MessageSerializer
from udew.settings import OPENAI_CHAT_HEADERS, OPENAI_QUESTIONS, OPENAI_ANSWERS
from api.chat_service import *


class MessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        profile = get_object_or_404(Profile, user=request.user)
        thread_id = profile.chat_thread_id

        message_objs = Message.objects.filter(user=request.user)

        chat = get_chat(thread_id)
        messages = []
        for m in reversed(message_objs):
            messages.append({"role": m.role, "content": m.content})

        return Response(data=reversed(chat + messages))

    def post(self, request, format=None):
        profile = get_object_or_404(Profile, user=request.user)
        thread_id = profile.chat_thread_id
        print(request.data)
        serializer = MessageSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        if serializer.data.get("content") in OPENAI_QUESTIONS:
            Message.objects.create(user=request.user, role="user", content=serializer.data.get("content"))
            return Response(data={"run_id": OPENAI_QUESTIONS[serializer.data.get("content")]})

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

        print(run_id)
        print(run_id in OPENAI_ANSWERS)
        if run_id in OPENAI_ANSWERS:
            Message.objects.create(user=request.user, role="assistant", content=OPENAI_ANSWERS[run_id])
            return Response(data={"status": "completed",
                                  "answer": {"role": "assistant", "content": OPENAI_ANSWERS[run_id]}})

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


class DefaultMessageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return Response(data=[key for key in OPENAI_QUESTIONS.keys()])
