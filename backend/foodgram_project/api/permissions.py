from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class IsAdminOrAuthorOrReadonly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'admin'
            or request.user.is_superuser
        )
