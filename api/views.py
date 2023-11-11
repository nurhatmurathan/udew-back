from django.shortcuts import render
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import GPTChatSerializer

load_dotenv()

class GPTChatAPIView(APIView):
    def post(self, request):
        pass
