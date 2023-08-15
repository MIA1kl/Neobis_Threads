from rest_framework.permissions import IsAuthenticated


class BaseUserProfileViewMixin:
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user.is_private = user.is_private
        return user
