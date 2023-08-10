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


class ThreadLikeView(generics.UpdateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        thread = self.get_object()
        user = request.user

        if user in thread.likes.all():
            thread.likes.remove(user)
        else:
            thread.likes.add(user)

        thread.likes_count = thread.likes.count()
        serializer = self.get_serializer(thread)
        return Response(serializer.data)
