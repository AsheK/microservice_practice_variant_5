# Этап 1: Сборщик (Builder)
FROM python:3.12-slim as builder

WORKDIR /build
RUN pip install grpcio-tools
RUN mkdir -p /build/protobufs/common/generated
COPY protobufs/common/generated/recommendations.proto /build/protobufs/common/generated/
RUN python -m grpc_tools.protoc \
    -I/build/protobufs \
    --python_out=/build \
    --grpc_python_out=/build \
    common/generated/recommendations.proto

# ---
# Этап 2: Финальный образ
FROM python:3.12-slim
ENV PYTHONPATH /app
WORKDIR /app

COPY marketplace/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем сгенерированный код из этапа сборки
COPY --from=builder /build/common/ /app/common/

# Копируем исходный код приложения
COPY marketplace/ /app/marketplace/

# Открываем порт для Flask
EXPOSE 5001

# Production-Ready Комментарий: Запуск приложения
# Вместо прямого вызова python, в production используется WSGI-сервер.
# Например, Gunicorn:
# ENTRYPOINT ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5001", "marketplace.marketplace:app"]
# Это требует добавления 'gunicorn' в requirements.txt
ENTRYPOINT ["python", "marketplace/marketplace.py"]