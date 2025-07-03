# Этап 1: Сборщик (Builder) - для компиляции .proto и установки зависимостей
# Использование многоэтапных сборок - это лучшая практика для уменьшения
# размера финального образа и повышения безопасности.
FROM python:3.12-slim as builder

WORKDIR /build

# Устанавливаем grpcio-tools только на этапе сборки
RUN pip install grpcio-tools protobuf

# Создаем структуру, которую будем использовать для импортов
COPY protobufs /build/protobufs/

# Генерируем код, указывая корень для импортов
RUN python -m grpc_tools.protoc \
    -I/build/protobufs \
    --python_out=/build \
    --grpc_python_out=/build \
    common/generated/recommendations.proto

# ---
# Этап 2: Финальный образ (Final Image)
FROM python:3.12-slim

# Устанавливаем PYTHONPATH, чтобы Python искал модули в /app
ENV PYTHONPATH /app

WORKDIR /app

# Копируем зависимости
COPY recommendations/requirements.txt .

# Устанавливаем только runtime зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем сгенерированный код из этапа сборки
COPY --from=builder /build/common/ /app/common/

# Копируем исходный код приложения и базу данных
COPY recommendations/ /app/recommendations/
COPY database/ /app/database/

# Открываем порт для gRPC
EXPOSE 50051

# Запускаем сервис
# Production-Ready Комментарий: Пользователь
# В production образы не должны запускаться от root. Следует создать
# непривилегированного пользователя и переключиться на него:
# RUN useradd --create-home appuser
# USER appuser
ENTRYPOINT ["python", "recommendations/recommendations.py"]