from django.db import models
from user.models import CustomUser


class Thread(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, default='')
    thread_picture = models.ImageField(upload_to='thread_pictures/', blank=True, null=True)
    author = models.ForeignKey(CustomUser, related_name='threads', on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, related_name='liked_threads', blank=True)


    class Meta:
        ordering = ['-created']
