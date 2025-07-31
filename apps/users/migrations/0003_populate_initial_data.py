# ИМПОРТИРУЕМ ФУНКЦИЮ ДЛЯ ХЭШИРОВАНИЯ ПАРОЛЕЙ
from django.contrib.auth.hashers import make_password
from django.db import migrations


def populate_initial_data(apps, schema_editor):
    """
    Заполняет базу данных начальными данными: разрешениями, ролями и пользователями.
    """
    permission_model = apps.get_model("users", "Permission")
    role_model = apps.get_model("users", "Role")
    user_model = apps.get_model("users", "CustomUser")

    # --- 1. Создание Разрешений (Permissions) ---
    perm_view_own_docs, _ = permission_model.objects.get_or_create(
        name="view_own_documents",
        defaults={
            "description": "Разрешает пользователю просматривать свои документы."
        },
    )
    perm_view_reports, _ = permission_model.objects.get_or_create(
        name="view_financial_reports",
        defaults={"description": "Разрешает просматривать финансовые отчеты."},
    )
    perm_manage_perms, _ = permission_model.objects.get_or_create(
        name="manage_permissions",
        defaults={"description": "Разрешает управлять разрешениями."},
    )
    perm_manage_roles, _ = permission_model.objects.get_or_create(
        name="manage_roles", defaults={"description": "Разрешает управлять ролями."}
    )
    perm_assign_roles, _ = permission_model.objects.get_or_create(
        name="assign_roles",
        defaults={"description": "Разрешает назначать роли пользователям."},
    )

    # --- 2. Создание Ролей (Roles) ---
    admin_role, created = role_model.objects.get_or_create(name="Администратор")
    if created:
        all_permissions = permission_model.objects.all()
        admin_role.permissions.set(all_permissions)

    user_role, created = role_model.objects.get_or_create(name="Пользователь")
    if created:
        user_role.permissions.set([perm_view_own_docs])

    # --- 3. Создание Пользователей (Users) - ФИНАЛЬНЫЙ РАБОЧИЙ СПОСОБ ---
    if not user_model.objects.filter(email="admin@example.com").exists():
        # Хэшируем пароль вручную
        hashed_password_admin = make_password("adminpassword123")
        admin_user = user_model.objects.create(
            email="admin@example.com",
            password=hashed_password_admin,  # Сохраняем уже хэш
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        admin_user.roles.add(admin_role)

    if not user_model.objects.filter(email="user@example.com").exists():
        # Хэшируем пароль вручную
        hashed_password_user = make_password("userpassword123")
        regular_user = user_model.objects.create(
            email="user@example.com",
            password=hashed_password_user,  # Сохраняем уже хэш
            first_name="Тестовый",
            last_name="Пользователь",
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )
        regular_user.roles.add(user_role)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_permission_role_customuser_roles"),
    ]

    operations = [
        migrations.RunPython(populate_initial_data),
    ]
