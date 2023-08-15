from django.contrib import admin
from thread.models import Thread, Like, CommentLike, Comment

admin.site.register(Thread)
admin.site.register(Like)
admin.site.register(CommentLike)
admin.site.register(Comment)
