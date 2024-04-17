from rest_framework import permissions


class IsAuthenticatedAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только авторизованным пользователям
    выполнять действия, изменяющие данные, но разрешая доступ
    только для чтения для всех пользователей.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение действия.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на действия над объектом.
        """
        return request.method in permissions.SAFE_METHODS or (
            obj.author == request.user
            or request.user.is_superuser
        )


class CreateOrAuthenticatedUser(permissions.BasePermission):
    """
    Позволяет создавать или аунтефикация.
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return True
        is_authenticated = request.user.is_authenticated
        is_safe_method = request.method in permissions.SAFE_METHODS
        return is_authenticated or is_safe_method
