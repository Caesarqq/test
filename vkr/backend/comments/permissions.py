from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешает только автору изменять или удалять комментарий.
    Чтение разрешено всем, создание — только авторизованным.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS (GET, HEAD, OPTIONS) — разрешены всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # POST (создание) — только авторизованным
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        # Остальные методы (PUT, PATCH, DELETE) — проверяются на объекте
        return True

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS — разрешены всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение и удаление — только автору
        return obj.user == request.user
