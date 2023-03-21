from rest_framework import permissions

from users.models import BlackListedToken


class IsCurrentUser(permissions.BasePermission):
    message = 'Доступ запрещен!'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsTokenValid(permissions.BasePermission):
    message = 'Доступ запрещен! Получите новый токен.'

    def has_permission(self, request, view):
        user_id = request.user.id
        is_allowed_user = True
        token = request.auth
        try:
            is_black_listed = BlackListedToken.objects.get(
                user=user_id,
                token=token
            )
            if is_black_listed:
                is_allowed_user = False
        except BlackListedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Доступ запрещен!'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
