from rest_framework import status, generics
from rest_framework.response import Response
from user.models import CustomUser
from django.db.models import Q
from django.http import Http404
from .models import Thread, Like, Comment, CommentLike
from .serializers import (
    ThreadSerializer,
    CommentSerializer,
    LikedUserSerializer,
    ThreadWithCommentSerializer,
    QuotationSerializer,
    RepostSerializer
)
import re
from rest_framework.permissions import IsAuthenticated
from user.models import FollowingSystem
from rest_framework.views import APIView
from .mixins import LikedUsersListMixin, ThreadQuerysetMixin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .mixins import LikedUsersListMixin
import cloudinary.uploader

class ThreadListView(generics.ListCreateAPIView, ThreadQuerysetMixin):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        thread = serializer.save(author=self.request.user)

        # Отправка обновления в WebSocket
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     'chat_group',
        #     {
        #         'type': 'update_thread',
        #         'data': ThreadSerializer(thread).data,
        #     }
        # )

class ThreadDetailView(generics.RetrieveAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]


class ThreadWithCommentListView(generics.ListCreateAPIView, ThreadQuerysetMixin):
    queryset = Thread.objects.all()
    serializer_class = ThreadWithCommentSerializer
    permission_classes = [IsAuthenticated]


class ThreadCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer

    def perform_create(self, serializer):
        content = self.request.data.get('content', '')  
        mentions = re.findall(r'@(\w+)', content)  

        thread = serializer.save(author=self.request.user)
        thread.mentioned_users.set(CustomUser.objects.filter(username__in=mentions))


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
    permission_classes = [IsAuthenticated]

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


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        comment = self.get_object()

        if comment.user == request.user or comment.thread.author == request.user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'You do not have permission to delete this comment'},
                            status=status.HTTP_403_FORBIDDEN)


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

class ThreadLikedUsersListView(LikedUsersListMixin, generics.ListAPIView):
    model = Thread
    lookup_field = 'thread_id'
    related_field = 'likes'


class CommentLikedUsersListView(LikedUsersListMixin, generics.ListAPIView):
    model = Comment
    lookup_field = 'comment_id'
    related_field = 'comment_likes'


class ThreadQuotationView(generics.CreateAPIView):
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        original_thread = serializer.validated_data['quoted_thread']
        quoted_content = serializer.validated_data.get('quoted_content', '')
        quoted_media = serializer.validated_data.get('quoted_media', None)

        new_thread = Thread.objects.create(
            author=self.request.user,
            content=quoted_content,
            thread_media=quoted_media,
            quoted_thread=original_thread,  

        )

        new_thread_serializer = ThreadSerializer(new_thread)
        return Response(new_thread_serializer.data, status=status.HTTP_201_CREATED)


class ThreadRepostView(generics.CreateAPIView):
    serializer_class = RepostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        original_thread = serializer.validated_data['quoted_thread']


        new_thread = Thread.objects.create(
            author=self.request.user,
            quoted_thread=original_thread,  

        )

        new_thread_serializer = ThreadSerializer(new_thread)
        return Response(new_thread_serializer.data, status=status.HTTP_201_CREATED)
    
class ThreadsByAuthorListView(generics.ListAPIView):
    serializer_class = ThreadWithCommentSerializer
    
    def get_queryset(self):
        author_email = self.kwargs['author_email']  
        author = CustomUser.objects.get(email=author_email)
        return Thread.objects.filter(author=author)


class ThreadsFromFollowedUsersView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followed_users = FollowingSystem.objects.filter(user_from=user).values_list('user_to', flat=True)
        return Thread.objects.filter(author__in=followed_users)
