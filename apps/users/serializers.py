from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser, Permission, Role


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    """

    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Повтор пароля"
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "label": "Пароль",
            }
        }

    def validate(self, data):
        """
        Проверяем, что два пароля совпадают.
        """
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        """
        Создаем нового пользователя.
        """
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            patronymic=validated_data.get("patronymic", ""),
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа пользователя.
    """

    email = serializers.EmailField(label="Email")
    password = serializers.CharField(
        label="Пароль", style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = "Невозможно войти с предоставленными учетными данными."
                raise serializers.ValidationError(msg, code="authorization")

            if not isinstance(user, CustomUser):
                msg = "Некорректный тип пользователя."
                raise serializers.ValidationError(msg, code="authorization")

            if user.is_deleted:
                msg = "Аккаунт этого пользователя удален."
                raise serializers.ValidationError(msg, code="authorization")

        else:
            msg = 'Необходимо указать "email" и "password".'
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя.
    Позволяет просматривать и обновлять данные.
    """

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "patronymic")

        read_only_fields = ("email",)


class PermissionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Разрешений."""

    class Meta:
        model = Permission
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ролей."""

    permissions = PermissionSerializer(many=True, read_only=True)

    permission_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "permission_ids"]

    def create(self, validated_data):
        permission_ids = validated_data.pop("permission_ids", [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop("permission_ids", None)
        instance = super().update(instance, validated_data)
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        return instance
