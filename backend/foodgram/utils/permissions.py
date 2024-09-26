from rest_framework.permissions import BasePermission, SAFE_METHODS


class CurrentUserAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated and request.user.is_staff
            or obj.pk == request.user.pk
        )


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.method in SAFE_METHODS
