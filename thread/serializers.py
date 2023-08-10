from thread.models import Thread, Like
from rest_framework import serializers


class ThreadSerializer(serializers.ModelSerializer):
    thread_picture = serializers.ImageField(required=False)
    likes = serializers.SerializerMethodField()
    author = serializers.StringRelatedField()  

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'likes', 'author'] 
    def get_likes(self, thread):
        return Like.objects.filter(thread=thread).count()

