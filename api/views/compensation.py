from rest_framework import generics
from api.models import ApplicationCompensation
from api.serializers.compensation import *
from rest_framework.permissions import IsAuthenticated


class ApplicationCompensationListCreateView(generics.ListCreateAPIView):
    queryset = ApplicationCompensation.objects.all()
    serializer_class = ApplicationCompensationPostSerializer
    permission_classes = [IsAuthenticated]
