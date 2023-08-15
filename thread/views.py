from rest_framework import status, generics
from rest_framework.response import Response
from django.db.models import Q
from .models import Thread, Like, Comment, CommentLike
from .serializers import (
    ThreadSerializer,
    CommentSerializer,
    LikedUserSerializer,
    ThreadWithCommentSerializer,
)
from rest_framework.permissions import IsAuthenticated
from user.models import CustomUser, FollowingSystem
from rest_framework.views import APIView
from .mixins import LikedUsersListMixin


class ThreadListView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user
        subscribed_u sers = FollowingSystem.objects.filter(user_from=user, is_approved=True).values_list('user_to', flat=True)
        return Thread.objects.filter(
            Q(author=user) |  # Показываем threads автора
            Q(author__in=subscribed_users) |  # Показываем threads авторов, на которых подписан пользователь и запрос подтвержден
            ~Q(author__is_private=True)  # Показываем public threads
        )


class ThreadDetailView(generics.RetrieveAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]


class ThreadWithCommentListView(generics.ListCreateAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadWithCommentSerializer
    # permission_classes = [IsAuthenticated]


class ThreadCreateView(generics.CreateAPIView):
    # permission_classes = [IsAuthenticated]
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


class ThreadDeleteView(generics.DestroyAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    # permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        thread = self.get_object()

        if thread.author != request.user:
            return Response({"detail": "You do not have permission to delete this thread."},
                            status=status.HTTP_403_FORBIDDEN)

        thread.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ThreadCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, thread_id, *args, **kwargs):
        try:
            thread = Thread.objects.get(pk=thread_id)
        except Thread.DoesNotExist:
            return Response({"detail": "Thread not found."}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content')
        parent_id = request.data.get('parent')

        if parent_id:
            try:
                parent_comment = Comment.objects.get(pk=parent_id)
            except Comment.DoesNotExist:
                return Response({"detail": "Parent comment not found."}, status=status.HTTP_404_NOT_FOUND)
            comment = Comment.objects.create(user=request.user, thread=thread, content=content, parent=parent_comment)
        else:
            comment = Comment.objects.create(user=request.user, thread=thread, content=content)

        comment_serializer = CommentSerializer(comment)
        return Response(comment_serializer.data, status=status.HTTP_201_CREATED)


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)

        if not created:
            like.delete()
            comment.likes -= 1
        else:
            comment.likes += 1

        comment.save()

        comment_serializer = CommentSerializer(comment)
        return Response(comment_serializer.data)
