# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем метаданные
LABEL maintainer="Balls Game"
LABEL description="Игра с шариками на Python и Tkinter"

# Устанавливаем системные зависимости для tkinter и X11
# Для Debian-based систем (python:3.11-slim основан на Debian)
RUN apt-get update && apt-get install -y \
    python3-tk \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY gui.py logic.py requirements.txt ./

# Устанавливаем зависимости Python (если есть)
# В данном случае requirements.txt содержит только комментарий,
# так как tkinter встроен в Python
RUN pip install --no-cache-dir -r requirements.txt || true

# Устанавливаем переменную окружения для X11 (можно переопределить при запуске)
ENV DISPLAY=:0

# Точка входа - запуск игры
CMD ["python", "gui.py"]

