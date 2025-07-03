# recommendations/recommendations.py
import os
from pathlib import Path
import grpc
import logging
import sqlite3
from concurrent import futures

import recommendations_pb2
import recommendations_pb2_grpc

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Находим абсолютный путь к директории, в которой находится текущий скрипт
script_dir = Path(__file__).resolve().parent
# Формируем абсолютный путь к файлу БД
DB_PATH = script_dir.parent / "database" / "books.db"
SCHEMA_PATH = script_dir.parent / "database" / "schema.sql"
SEED_PATH = script_dir.parent / "database" / "seed.sql"

# Production-Ready Комментарий: Управление конфигурацией
# В реальных системах путь к БД и другие параметры конфигурации
# не должны быть захардкожены. Их следует получать из переменных окружения
# или конфигурационных файлов (например, .env, .yaml).
# Пример:
# DB_PATH = os.getenv("RECOMMENDATIONS_DB_PATH", default_db_path)
# Это позволяет гибко настраивать сервис для разных окружений (dev, staging, prod)
# без изменения кода.

def get_db_connection():
    """ Устанавливает соединение с БД SQLite. """
    logger.debug(f"Connecting to database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class RecommendationService(recommendations_pb2_grpc.RecommendationsServicer):
    """
    gRPC сервис, предоставляющий рекомендации по книгам.
    """

    def Recommend(self, request: recommendations_pb2.RecommendationRequest,
                  context) -> recommendations_pb2.RecommendationResponse:
        logger.info(
            f"Received request for category {recommendations_pb2.BookCategory.Name(request.category)} "
            f"with max_results={request.max_results}"
        )
        # Production-Ready Комментарий: Обработка ошибок
        # В реальной системе здесь бы стоял более сложный блок try/except/finally
        # для гарантии закрытия соединения с БД и обработки специфичных ошибок БД
        # (например, OperationalError), возможно, с использованием паттерна Retry.
        conn = get_db_connection()
        cursor = conn.cursor()

        # Production-Ready Комментарий: Доступ к данным
        # Этот код напрямую работает с SQL. В больших системах это выносится
        # в отдельный Слой Доступа к Данным (DAL), например, с использованием
        # паттерна Repository, чтобы изолировать бизнес-логику от деталей работы с БД.
        # Также могли бы использоваться ORM типа SQLAlchemy.
        try:
            # Используем параметризованный запрос для безопасности (защита от SQL-инъекций)
            # ORDER BY RANDOM() LIMIT ? - эффективный способ получить случайные записи в SQLite
            cursor.execute(
                "SELECT id, title FROM books WHERE category_id = ? ORDER BY RANDOM() LIMIT ?",
                (request.category, request.max_results)
            )
            books = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, "Database error occurred")
            return recommendations_pb2.RecommendationResponse()
        finally:
            conn.close()

        recommendations = [
            recommendations_pb2.BookRecommendation(id=row['id'], title=row['title'])
            for row in books
        ]

        logger.info(f"Returning {len(recommendations)} recommendations.")
        return recommendations_pb2.RecommendationResponse(recommendations=recommendations)


def serve():
    """ Запускает gRPC сервер. """
    # Production-Ready Комментарий: Управление ресурсами
    # max_workers=10 - это простая настройка. В production-системе количество воркеров
    # подбирается на основе профилирования нагрузки и характеристик CPU.
    # Для CPU-bound задач ~ кол-во ядер. Для IO-bound - значительно больше.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
        RecommendationService(), server
    )

    # Production-Ready Комментарий: Безопасность
    # add_insecure_port - используется только для разработки.
    # В production необходимо использовать server.add_secure_port()
    # с SSL/TLS сертификатами для шифрования трафика.
    server.add_insecure_port("[::]:50051")

    logger.info(f"Starting Recommendations service on port 50051...")
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)


if __name__ == '__main__':
    # Production-Ready Комментарий: Инициализация БД
    # Этот блок создает и наполняет БД при первом запуске, если она отсутствует.
    # В реальных проектах для этого используются системы миграций (например, Alembic).
    if not os.path.exists(DB_PATH):
        logger.info("Database not found. Initializing...")
        try:
            # Убедимся, что директория существует
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            conn = get_db_connection()
            with open(SCHEMA_PATH) as f:
                conn.executescript(f.read())
            with open(SEED_PATH) as f:
                conn.executescript(f.read())
            conn.close()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            exit(1)  # Завершаем работу, если БД не создалась

    serve()