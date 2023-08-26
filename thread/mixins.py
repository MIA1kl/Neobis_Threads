from rest_framework.permissions import IsAuthenticated
from user.models import CustomUser
from .serializers import LikedUserSerializer


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
