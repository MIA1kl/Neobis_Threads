from thread.models import Thread, Like, Comment
from rest_framework import serializers
import cloudinary
from user.models import CustomUser
from cloudinary.uploader import upload

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    replies = serializers.SerializerMethodField()
    created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    likes = serializers.SerializerMethodField()
    thread_content = serializers.SerializerMethodField()  

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created', 'likes', 'parent', 'replies', 'thread_content']  

    def get_replies(self, comment):
        replies = Comment.objects.filter(parent=comment)
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def get_likes(self, comment):
        return comment.comment_likes.count()

    def get_thread_content(self, comment):  
        return comment.thread.content if comment.thread else None



class ThreadSerializer(serializers.ModelSerializer):
    thread_media = serializers.FileField(required=False)
    likes = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()
    quoted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all(), required=False)
    username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_media', 'author', 'username', 'created','likes', 'comments_count', 'quoted_thread']

    def get_likes(self, thread):
        return Like.objects.filter(thread=thread).count()

    def get_comments_count(self, thread):
        return Comment.objects.filter(thread=thread).count()
    
    def create(self, validated_data):
        thread_media = validated_data.pop('thread_media', None)

        thread = Thread.objects.create(**validated_data)

        if thread_media:
            uploaded_media = upload(thread_media)
            
            # Update the thread's media URL with the Cloudinary URL
            thread.thread_media = uploaded_media['url']
            thread.save()

        return thread



class LikedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'name', 'profile_picture')


class ThreadWithCommentSerializer(ThreadSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)


    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_media', 'author', 'username', 'created','likes', 'comments_count', 'comments']


class QuotationSerializer(serializers.ModelSerializer):
    quoted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all()) 
    quoted_content = serializers.CharField(max_length=200,required=False, allow_blank=True)
    quoted_media = serializers.FileField(required=False)

    class Meta:
        model = Thread
        fields = ['quoted_thread', 'quoted_content', 'quoted_media']
        
    def create(self, validated_data):
        quoted_media = validated_data.get('quoted_media')
        
        if quoted_media:
            validated_data['quoted_media'] = self.upload_and_compress_media(quoted_media)

        return super().create(validated_data)


class RepostSerializer(serializers.ModelSerializer):
    quoted_thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all()) 

    class Meta:
        model = Thread
        fields = ['quoted_thread']