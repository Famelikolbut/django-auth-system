# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в рабочую директорию
COPY . .

# Открываем порт 8000 для доступа к приложению
EXPOSE 8000

# Команда, которая будет выполняться при запуске контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]