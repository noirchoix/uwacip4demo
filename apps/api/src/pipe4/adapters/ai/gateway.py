from __future__ import annotations

import httpx

from pipe4.exceptions import ExternalDependencyUnavailable
from pipe4.ports.ai import AIInterpretation


class HttpAIGatewayAdapter:
    """Provider-neutral typed AI gateway. Model vendors remain outside Pipe 4."""

    def __init__(self, *, url: str, token: str | None, timeout_seconds: float = 8.0) -> None:
        self.url = url.rstrip("/")
        self.token = token
        self.timeout = timeout_seconds

    async def interpret(self, *, text: str, latitude: float | None, longitude: float | None) -> AIInterpretation:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.url}/interpret-current-reality",
                    json={"text": text, "latitude": latitude, "longitude": longitude},
                    headers=headers,
                )
                response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            raise ExternalDependencyUnavailable("AI gateway is unavailable") from exc
        return AIInterpretation.model_validate(response.json())


class UnavailableAIAdapter:
    async def interpret(self, *, text: str, latitude: float | None, longitude: float | None) -> AIInterpretation:
        raise ExternalDependencyUnavailable("AI interpretation is not configured")
