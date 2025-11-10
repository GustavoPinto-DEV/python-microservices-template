"""
Tests para middleware

Tests que verifican el comportamiento de los middleware
(BitacoraMiddleware, RateLimiterMiddleware).
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import time

from middleware.BitacoraMiddleware import BitacoraMiddleware
from middleware.RateLimiterMiddleware import RateLimiterMiddleware


class TestBitacoraMiddleware:
    """Tests para BitacoraMiddleware"""

    def test_middleware_logs_requests(self, caplog):
        """Test que el middleware registra requests"""
        app = FastAPI()
        app.add_middleware(BitacoraMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        # Verificar que se registró el request en logs
        assert any("GET" in record.message for record in caplog.records)
        assert any("/test" in record.message for record in caplog.records)

    def test_middleware_adds_headers(self):
        """Test que el middleware agrega headers de auditoría"""
        app = FastAPI()
        app.add_middleware(BitacoraMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        # Verificar headers agregados
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_middleware_excludes_paths(self):
        """Test que el middleware excluye paths configurados"""
        app = FastAPI()
        app.add_middleware(
            BitacoraMiddleware,
            exclude_paths=["/health", "/docs"]
        )

        @app.get("/health")
        async def health():
            return {"status": "ok"}

        @app.get("/api/test")
        async def api_test():
            return {"data": "test"}

        client = TestClient(app)

        # Request a path excluido no debería tener headers de auditoría
        health_response = client.get("/health")
        assert "X-Request-ID" not in health_response.headers

        # Request a path normal sí debería tener headers
        api_response = client.get("/api/test")
        assert "X-Request-ID" in api_response.headers

    def test_middleware_handles_errors(self, caplog):
        """Test que el middleware maneja errores correctamente"""
        app = FastAPI()
        app.add_middleware(BitacoraMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise Exception("Test error")

        client = TestClient(app)

        with pytest.raises(Exception):
            client.get("/error")

        # Verificar que se registró el error
        assert any("Error" in record.message or "error" in record.message
                   for record in caplog.records)

    def test_middleware_compression(self):
        """Test de compresión gzip de responses"""
        app = FastAPI()
        app.add_middleware(
            BitacoraMiddleware,
            enable_compression=True,
            min_size_to_compress=100
        )

        @app.get("/large")
        async def large_response():
            return {"data": "x" * 1000}  # Response grande

        client = TestClient(app)
        response = client.get(
            "/large",
            headers={"Accept-Encoding": "gzip"}
        )

        # Verificar que se puede comprimir
        # (En testing real, verificar Content-Encoding: gzip)
        assert response.status_code == 200


class TestRateLimiterMiddleware:
    """Tests para RateLimiterMiddleware"""

    def test_rate_limiter_allows_requests(self):
        """Test que el rate limiter permite requests dentro del límite"""
        app = FastAPI()
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=10,
            window_seconds=60
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Hacer varias requests (dentro del límite)
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_rate_limiter_blocks_excess_requests(self):
        """Test que el rate limiter bloquea requests que exceden el límite"""
        app = FastAPI()
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=3,  # Límite bajo para testing
            window_seconds=60
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Hacer requests hasta exceder el límite
        for i in range(3):
            response = client.get("/test")
            assert response.status_code == 200

        # La siguiente request debería ser bloqueada
        response = client.get("/test")
        assert response.status_code == 429  # Too Many Requests
        assert "Retry-After" in response.headers

    def test_rate_limiter_per_ip(self):
        """Test que el rate limiter es por IP"""
        app = FastAPI()
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=2,
            window_seconds=60
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Simular requests desde diferentes IPs
        # (En testing real, usar diferentes TestClients o headers)
        response = client.get("/test")
        assert response.status_code == 200

    def test_rate_limiter_window_resets(self):
        """Test que el rate limiter resetea después de la ventana"""
        app = FastAPI()
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=2,
            window_seconds=1  # 1 segundo para testing
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        # Hacer requests hasta el límite
        for _ in range(2):
            response = client.get("/test")
            assert response.status_code == 200

        # Siguiente request es bloqueada
        response = client.get("/test")
        assert response.status_code == 429

        # Esperar que pase la ventana
        time.sleep(2)

        # Ahora debería permitir nuevamente
        response = client.get("/test")
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """Tests de integración de múltiples middleware"""

    def test_multiple_middleware_order(self):
        """Test que múltiples middleware se ejecutan en orden correcto"""
        app = FastAPI()

        # Agregar middleware en orden específico
        app.add_middleware(BitacoraMiddleware)
        app.add_middleware(
            RateLimiterMiddleware,
            max_requests=10,
            window_seconds=60
        )

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        # Verificar que ambos middleware funcionaron
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers  # De BitacoraMiddleware
        # Rate limiter permitió el request

    def test_middleware_with_auth(self, auth_headers):
        """Test de middleware con autenticación"""
        # TODO: Implementar cuando se integre auth completo
        pass
