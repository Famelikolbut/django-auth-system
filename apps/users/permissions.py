from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """
    Кастомный класс разрешений для проверки доступа на основе моделей Role и Permission.
    """

    message = "У вас нет разрешения на выполнение этого действия."

    def has_permission(self, request, view):
        # 1. Сначала базовая проверка, аутентифицирован ли пользователь вообще.
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Суперпользователю разрешено всё. Это стандартная практика.
        if request.user.is_superuser:
            return True

        # 3. Получаем список кодовых имен разрешений,
        # которые требуются для доступа к этой View.
        #    Мы будем определять этот список прямо в наших View (см. Шаг 6).
        required_permissions = getattr(view, "required_permissions", [])

        # 4. Если для View не указаны specific permissions, то доступ разрешен любому
        #    аутентифицированному пользователю.
        if not required_permissions:
            return True

        # 5. Получаем все разрешения, которые есть у пользователя через его роли.
        #    Используем set для быстрой проверки и избежания дубликатов.
        user_permissions = set()

        # Проходим по всем ролям пользователя
        for role in request.user.roles.all():
            # Проходим по всем разрешениям в каждой роли
            for perm in role.permissions.all():
                user_permissions.add(perm.name)

        # 6. Проверяем, есть ли у пользователя хотя бы одно
        # из требуемых разрешений.
        #    Мы ищем пересечение множества разрешений пользователя
        #    и множества требуемых разрешений.
        if not user_permissions.intersection(required_permissions):
            # Если пересечения нет, значит, ни одного нужного права
            # у пользователя нет.
            return False

        # Если все проверки пройдены, даем доступ.
        return True
