from rest_framework.permissions import IsAuthenticated
from user.models import CustomUser
from .serializers import LikedUserSerializer
from django.db.models import Q
from thread.models import Thread
from user.models import FollowingSystem


class LikedUsersListMixin:
    serializer_class = LikedUserSerializer
    permission_classes = [IsAuthenticated]
    model = None
    lookup_field = None
    related_field = None

    def get_queryset(self):
        obj_id = self.kwargs[self.lookup_field]
        try:
            obj = self.model.objects.get(id=obj_id)
            liked_users = CustomUser.objects.filter(**{f'{self.related_field}__{self.lookup_field}': obj})
            return liked_users
        except self.model.DoesNotExist:
            return CustomUser.objects.none()


class ThreadQuerysetMixin:
    def get_queryset(self):
        user = self.request.user
        subscribed_users = FollowingSystem.objects.filter(user_from=user, is_approved=True).values_list('user_to',
                                                                                                        flat=True)
        return Thread.objects.filter(
            Q(author=user) |
            Q(author__in=subscribed_users) |
            ~Q(author__is_private=True)
        )
