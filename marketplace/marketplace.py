# marketplace/marketplace.py
import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv
import grpc

# Импортируем из общего сгенерированного пакета
from common.generated import recommendations_pb2, recommendations_pb2_grpc

# Загружаем переменные окружения из .env файла для локальной разработки
load_dotenv()

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Production-Ready Комментарий: Управление конфигурацией
# Использование os.getenv позволяет гибко настраивать приложение через переменные окружения,
# что является стандартом для облачных и контейнеризированных приложений (Twelve-Factor App).
RECOMMENDATIONS_HOST = os.getenv("RECOMMENDATIONS_HOST", "localhost")
RECOMMENDATIONS_PORT = 50051

# Карта для отображения человекочитаемых имен категорий
CATEGORY_NAMES = {
    v.number: v.name.replace("_", " ").title()
    for v in recommendations_pb2.BookCategory.DESCRIPTOR.values
}


@app.route("/")
def render_homepage():
    # --- Индивидуальный вариант №5 ---
    category_for_request = recommendations_pb2.BookCategory.SCIENCE_FICTION
    max_results_for_request = 2
    # --- Конец применения варианта ---

    category_name_display = CATEGORY_NAMES.get(category_for_request, "Неизвестная категория")
    recommendations_list = []
    error_message = None

    try:
        # Production-Ready Комментарий: Управление соединениями (gRPC Channel)
        # Создание канала на каждый запрос - неэффективно. В реальном приложении
        # канал должен быть создан один раз при старте приложения и переиспользоваться.
        # Однако, это требует более сложного управления состоянием и обработки
        # разрыва соединения (например, с помощью паттерна Singleton или DI-контейнера).
        logger.info(f"Connecting to Recommendations service at {RECOMMENDATIONS_HOST}:{RECOMMENDATIONS_PORT}")
        with grpc.insecure_channel(f"{RECOMMENDATIONS_HOST}:{RECOMMENDATIONS_PORT}") as channel:
            client = recommendations_pb2_grpc.RecommendationsStub(channel)

            request = recommendations_pb2.RecommendationRequest(
                user_id=1,
                category=category_for_request,
                max_results=max_results_for_request
            )

            logger.info(f"Requesting recommendations: {request.category}, {request.max_results}")
            response = client.Recommend(request, timeout=5.0)
            recommendations_list = response.recommendations
            logger.info(f"Received {len(recommendations_list)} recommendations.")

    except grpc.RpcError as e:
        logger.error(f"gRPC call failed: {e.details()} (Code: {e.code()})")
        # Production-Ready Комментарий: Отказоустойчивость
        # Здесь можно реализовать паттерны Circuit Breaker и Retry.
        # Например, при коде UNAVAILABLE можно сделать несколько повторных попыток
        # с экспоненциальной задержкой. Если ошибки продолжаются, "размыкаем" Circuit Breaker,
        # чтобы не нагружать неработающий сервис, и сразу отдаем ошибку/данные из кэша.
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            error_message = "Сервис рекомендаций временно недоступен. Пожалуйста, попробуйте позже."
        elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            error_message = "Сервис рекомендаций не ответил вовремя. Пожалуйста, попробуйте позже."
        else:
            error_message = f"Произошла ошибка при получении рекомендаций."
    except Exception as e:
        logger.error(f"An unexpected error occurred in Marketplace: {e}", exc_info=True)
        error_message = "Произошла внутренняя ошибка сервера."

    return render_template(
        "homepage.html",
        recommendations=recommendations_list,
        error=error_message,
        category_name=category_name_display,
    )


if __name__ == '__main__':
    # Production-Ready Комментарий: WSGI Сервер
    # Встроенный сервер Flask подходит только для разработки.
    # В production следует использовать полноценный WSGI сервер, например, Gunicorn или uWSGI,
    # который запускается несколькими воркерами и обычно стоит за reverse-proxy (Nginx).
    # Пример запуска в production: gunicorn --workers 4 --bind 0.0.0.0:5001 marketplace:app
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=os.getenv("FLASK_DEBUG", "False").lower() in ['true', '1', 't']
    )