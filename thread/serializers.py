from thread.models import Thread
from rest_framework import serializers


class ThreadSerializer(serializers.ModelSerializer):
    thread_picture = serializers.ImageField(required=False)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'content', 'thread_picture', 'liked_by_user']

    def get_liked_by_user(self, instance):
        user = self.context['request'].user
        return user in instance.likes.all()
