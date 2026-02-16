FROM python:3.14-slim

# Запрещаем Python писать pyc файлы
ENV PYTHONDONTWRITEBYTECODE=1
# Запрещаем буферизацию вывода (чтобы логи сразу летели в консоль Docker)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Разворачиваем остальное
COPY . .
RUN mkdir -p files

# Точка входа - запуск скрипта
CMD ["python", "main.py"]