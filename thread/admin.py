from django.contrib import admin
from thread.models import Thread, Like, CommentLike

admin.site.register(Thread)
admin.site.register(Like)
admin.site.register(CommentLike)
