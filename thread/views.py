from rest_framework import status, generics
from rest_framework.response import Response
from .models import Thread, Like
from .serializers import ThreadSerializer
from rest_framework.permissions import IsAuthenticated
from user.models import CustomUser
from rest_framework.views import APIView


class ThreadListView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]


class ThreadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ThreadLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, thread_id, *args, **kwargs):
        try:
            thread = Thread.objects.get(pk=thread_id)
        except Thread.DoesNotExist:
            return Response({"detail": "Thread not found."}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(user=request.user, thread=thread)

        if not created:
            like.delete()

        thread_serializer = ThreadSerializer(thread)
        return Response(thread_serializer.data)


