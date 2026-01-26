from __future__ import annotations

import unittest
from unittest.mock import patch

import httpx

from app.core.settings import settings
from app.services import openrouter_service


class _DummyResponse:
    def __init__(self, *, status_code: int, json_data=None, json_exc: Exception | None = None):
        self.status_code = status_code
        self._json_data = json_data
        self._json_exc = json_exc

    def json(self):
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_data


class _DummyAsyncClient:
    def __init__(self, *, response: _DummyResponse | None = None, exc: Exception | None = None):
        self._response = response
        self._exc = exc

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, *, headers=None, json=None):
        if self._exc is not None:
            raise self._exc
        return self._response


class OpenRouterServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self._prev_api_key = settings.openrouter_api_key
        self._prev_base_url = settings.openrouter_base_url
        self._prev_model = settings.openrouter_model
        self._prev_timeout = settings.openrouter_timeout_seconds

        settings.openrouter_api_key = "test-key"
        settings.openrouter_base_url = "https://example.invalid/api/v1"
        settings.openrouter_model = "openai/gpt-4o-mini"
        settings.openrouter_timeout_seconds = 0.1

    def tearDown(self) -> None:
        settings.openrouter_api_key = self._prev_api_key
        settings.openrouter_base_url = self._prev_base_url
        settings.openrouter_model = self._prev_model
        settings.openrouter_timeout_seconds = self._prev_timeout

    async def test_chat_completion_success(self) -> None:
        dummy = _DummyAsyncClient(
            response=_DummyResponse(
                status_code=200,
                json_data={
                    "choices": [
                        {
                            "message": {
                                "content": "Pong!",
                            }
                        }
                    ]
                },
            )
        )

        with patch.object(httpx, "AsyncClient", return_value=dummy):
            data = await openrouter_service.chat_completion(
                messages=[{"role": "user", "content": "ping"}],
            )

        self.assertEqual(data["choices"][0]["message"]["content"], "Pong!")

    async def test_chat_completion_auth_error(self) -> None:
        dummy = _DummyAsyncClient(response=_DummyResponse(status_code=401, json_data={}))
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterAuthError):
                await openrouter_service.chat_completion(
                    messages=[{"role": "user", "content": "ping"}],
                )

    async def test_chat_completion_rate_limit(self) -> None:
        dummy = _DummyAsyncClient(response=_DummyResponse(status_code=429, json_data={}))
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterRateLimitError):
                await openrouter_service.chat_completion(
                    messages=[{"role": "user", "content": "ping"}],
                )

    async def test_chat_completion_timeout(self) -> None:
        dummy = _DummyAsyncClient(exc=httpx.TimeoutException("timeout"))
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterTimeoutError):
                await openrouter_service.chat_completion(
                    messages=[{"role": "user", "content": "ping"}],
                )

    async def test_chat_completion_invalid_json(self) -> None:
        dummy = _DummyAsyncClient(
            response=_DummyResponse(status_code=200, json_exc=ValueError("not json"))
        )
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterInvalidResponseError):
                await openrouter_service.chat_completion(
                    messages=[{"role": "user", "content": "ping"}],
                )

    async def test_chat_completion_invalid_shape(self) -> None:
        dummy = _DummyAsyncClient(response=_DummyResponse(status_code=200, json_data={"x": 1}))
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterInvalidResponseError):
                await openrouter_service.chat_completion(
                    messages=[{"role": "user", "content": "ping"}],
                )

    async def test_structured_output_parses_json_object(self) -> None:
        dummy = _DummyAsyncClient(
            response=_DummyResponse(
                status_code=200,
                json_data={
                    "choices": [
                        {
                            "message": {
                                "content": "{\"ok\": true}",
                            }
                        }
                    ]
                },
            )
        )
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            parsed = await openrouter_service.structured_output(
                messages=[{"role": "user", "content": "ping"}],
                schema_name="test",
                json_schema={"type": "object", "properties": {"ok": {"type": "boolean"}}},
            )

        self.assertEqual(parsed, {"ok": True})

    async def test_structured_output_rejects_non_object(self) -> None:
        dummy = _DummyAsyncClient(
            response=_DummyResponse(
                status_code=200,
                json_data={
                    "choices": [
                        {
                            "message": {
                                "content": "[1, 2, 3]",
                            }
                        }
                    ]
                },
            )
        )
        with patch.object(httpx, "AsyncClient", return_value=dummy):
            with self.assertRaises(openrouter_service.OpenRouterInvalidResponseError):
                await openrouter_service.structured_output(
                    messages=[{"role": "user", "content": "ping"}],
                    schema_name="test",
                    json_schema={"type": "array"},
                )


if __name__ == "__main__":
    unittest.main()
