from thread.models import Thread
from rest_framework import serializers


class ThreadSerializer(serializers.ModelSerializer):
    thread_picture = serializers.ImageField(required=False)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'likes_count']

    def get_likes_count(self, instance):
        return instance.likes.count()
