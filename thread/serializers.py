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
    quoted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all(), required=False)


    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'author', 'likes', 'comments_count', 'quoted_thread']

    def get_likes(self, thread):
        return Like.objects.filter(thread=thread).count()

    def get_comments_count(self, thread):
        return Comment.objects.filter(thread=thread).count()




class LikedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'name', 'profile_picture')


class ThreadWithCommentSerializer(ThreadSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'author', 'likes', 'comments_count', 'comments']


class QuotationSerializer(serializers.ModelSerializer):
    quoted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all()) 
    quoted_content = serializers.CharField(required=False, allow_blank=True)
    quoted_image = serializers.ImageField(required=False)

    class Meta:
        model = Thread
        fields = ['quoted_thread', 'quoted_content', 'quoted_image']


