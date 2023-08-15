from thread.models import Thread, Like, Comment
from rest_framework import serializers

from user.models import CustomUser


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created', 'likes', 'parent', 'replies']

    def get_replies(self, comment):
        replies = Comment.objects.filter(parent=comment)
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def get_likes(self, comment):
        return comment.comment_likes.count()


class ThreadSerializer(serializers.ModelSerializer):
    thread_picture = serializers.ImageField(required=False)
    likes = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()
    reposted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all(), required=False)
    quoted_content = serializers.CharField(required=False, allow_blank=True)
    quoted_image = serializers.ImageField(required=False)

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'author', 'likes', 'comments']

    def get_likes(self, thread):
        return Like.objects.filter(thread=thread).count()
