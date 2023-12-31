from django.db import models
from user.models import CustomUser
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from cloudinary_storage.validators import validate_video


class Thread(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=280,blank=True, default='')
    thread_media = models.FileField(upload_to='thread_media/', blank=True, null=True)
    thread_video = models.FileField(upload_to='thread_videos/', blank=True, storage=VideoMediaCloudinaryStorage(),
                              validators=[validate_video])
    author = models.ForeignKey(CustomUser, related_name='threads', on_delete=models.CASCADE)
    likes = models.ManyToManyField(CustomUser, through='Like', related_name='liked_threads')
    mentioned_users = models.ManyToManyField(CustomUser, related_name='mentioned_in_threads', blank=True)
    quoted_thread = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')


    class Meta:
        ordering = ['-created']


class Like(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='liked_threads', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'thread']


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    mentions = models.ManyToManyField(CustomUser, related_name='mentioned_in_comments', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)


class CommentLike(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comment_likes', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='comment_likes', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'comment']
