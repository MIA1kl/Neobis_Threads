from django.db import models
from user.models import CustomUser


class Thread(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, default='')
    thread_picture = models.ImageField(upload_to='thread_pictures/', blank=True, null=True)
    author = models.ForeignKey(CustomUser, related_name='threads', on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, through='Like', related_name='liked_threads')

    class Meta:
        ordering = ['-created']


class Like(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='liked_threads', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'thread']
