from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.permissions import HasPermission

from .models import CustomUser, Permission, Role
from .serializers import (
    LoginSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    """
    View для регистрации пользователей.
    Доступно всем (AllowAny).
    """

    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class LoginView(generics.GenericAPIView):
    """
    View для входа в систему.
    Возвращает access и refresh токены.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class LogoutView(views.APIView):
    """
    View для выхода из системы.
    """

    permission_classes = [IsAuthenticated]


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    View для управления профилем пользователя.
    Доступно только аутентифицированным пользователям.
    - GET: получить данные своего профиля.
    - PUT/PATCH: обновить данные профиля.
    - DELETE: "мягко" удалить свой аккаунт.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Переопределяем метод, чтобы он всегда возвращал
        текущего залогиненного пользователя.
        """
        return self.request.user

    def perform_destroy(self, instance):
        """
        Переопределяем метод удаления для "мягкого" удаления.
        """
        # Пользователь инициирует удаление, происходит logout,
        instance.is_deleted = True
        instance.is_active = False
        instance.save()


class PermissionViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления Разрешениями.
    Доступно только администраторам с правом 'manage_permissions'.
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ["manage_permissions"]


class RoleViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления Ролями.
    Доступно только администраторам с правом 'manage_roles'.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ["manage_roles"]


class UserRoleAssignmentView(APIView):
    """
    View для назначения и снятия ролей с пользователей.
    Доступно только администраторам с правом 'assign_roles'.
    """

    permission_classes = [IsAuthenticated, HasPermission]
    required_permissions = ["assign_roles"]

    def _get_user_and_role(self, request_data):
        """
        Приватный метод для извлечения пользователя и роли из данных запроса.
        """
        _ = self.permission_classes
        user_id = request_data.get("user_id")
        role_id = request_data.get("role_id")

        if not user_id or not role_id:
            raise ValidationError(
                {"error": "Необходимо предоставить user_id и role_id"}
            )

        user = get_object_or_404(CustomUser, id=user_id)
        role = get_object_or_404(Role, id=role_id)

        return user, role

    def post(self, request, *args, **kwargs):
        """Назначить роль пользователю."""
        _ = self.permission_classes

        try:
            user, role = self._get_user_and_role(request.data)

        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        user.roles.add(role)

        return Response(
            {
                "message": f"Роль '{role.name}' успешно"
                f" назначена пользователю '{user.email}'"
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """Снять роль с пользователя."""
        _ = self.permission_classes

        try:
            user, role = self._get_user_and_role(request.data)
        # И ЗДЕСЬ
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        user.roles.remove(role)

        return Response(
            {
                "message": f"Роль '{role.name}' успешно снята"
                f" с пользователя '{user.email}'"
            },
            status=status.HTTP_200_OK,
        )
