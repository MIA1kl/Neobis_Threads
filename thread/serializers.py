from thread.models import Thread, Like, Comment
from rest_framework import serializers


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
    comments = CommentSerializer(many=True, read_only=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'author', 'likes', 'comments']

    def get_likes(self, thread):
        return Like.objects.filter(thread=thread).count()
