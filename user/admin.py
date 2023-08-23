from django.contrib import admin

from .models import CustomUser, FollowingSystem


admin.site.register(CustomUser)
admin.site.register(FollowingSystem)
