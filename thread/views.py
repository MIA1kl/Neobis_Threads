from rest_framework import status, generics
from rest_framework.response import Response
from .models import Thread
from .serializers import ThreadSerializer
from rest_framework.permissions import IsAuthenticated
from user.models import CustomUser

class ThreadListView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated] 

class ThreadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)  

