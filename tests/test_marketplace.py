import unittest
from unittest.mock import patch
import grpc

from marketplace.marketplace import app
from common.generated import recommendations_pb2


class MarketplaceTestCase(unittest.TestCase):
    """Тесты для веб-приложения Marketplace."""

    def setUp(self):
        """Настройка тестового клиента Flask перед каждым тестом."""
        app.config.update({"TESTING": True})
        self.client = app.test_client()

    # ИЗМЕНЯЕМ ЦЕЛЬ ДЛЯ PATCH
    @patch('marketplace.marketplace.recommendations_pb2_grpc.RecommendationsStub')
    def test_homepage_success(self, MockRecommendationsStub):
        """Тест успешного отображения рекомендаций на главной странице."""
        # Настраиваем возвращаемое значение для мока
        mock_stub_instance = MockRecommendationsStub.return_value
        mock_response = recommendations_pb2.RecommendationResponse(
            recommendations=[
                recommendations_pb2.BookRecommendation(id=11, title="Дюна"),
                recommendations_pb2.BookRecommendation(id=12, title="Игра Эндера"),
            ]
        )
        mock_stub_instance.Recommend.return_value = mock_response

        response = self.client.get('/')

        # Проверяем результат
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        self.assertIn("Дюна", response_text)
        self.assertIn("Игра Эндера", response_text)
        self.assertNotIn('class="error"', response_text)

    # ИЗМЕНЯЕМ ЦЕЛЬ ДЛЯ PATCH
    @patch('marketplace.marketplace.recommendations_pb2_grpc.RecommendationsStub')
    def test_homepage_grpc_unavailable(self, MockRecommendationsStub):
        """Тест обработки ошибки, когда сервис рекомендаций недоступен."""
        # Настраиваем мок, чтобы он вызывал ошибку
        mock_stub_instance = MockRecommendationsStub.return_value

        rpc_error = grpc.RpcError()
        rpc_error.code = lambda: grpc.StatusCode.UNAVAILABLE
        rpc_error.details = lambda: "Mocked service unavailable"
        mock_stub_instance.Recommend.side_effect = rpc_error

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn("Сервис рекомендаций временно недоступен", response.data.decode('utf-8'))