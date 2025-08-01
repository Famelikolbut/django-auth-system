from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """
    Кастомный класс разрешений для проверки доступа на основе моделей Role и Permission.
    """

    message = "У вас нет разрешения на выполнение этого действия."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        required_permissions = getattr(view, "required_permissions", [])

        if not required_permissions:
            return True

        user_permissions = set()

        for role in request.user.roles.all():
            for perm in role.permissions.all():
                user_permissions.add(perm.name)

        if not user_permissions.intersection(required_permissions):
            return False

        return True
