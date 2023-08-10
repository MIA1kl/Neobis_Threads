from thread.models import Thread
from rest_framework import serializers


class ThreadSerializer(serializers.ModelSerializer):
    thread_picture = serializers.ImageField(required=False) 

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture']
