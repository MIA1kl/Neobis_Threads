from rest_framework.permissions import IsAuthenticated

# from user.permissions import IsFollowerOrReadOnly


class BaseUserProfileViewMixin:
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user.is_private = user.is_private
        return user

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
