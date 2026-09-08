from __future__ import annotations

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    HTTP_REQUESTS = Counter(
        "pipe4_http_requests_total",
        "Pipe 4 HTTP requests",
        ["method", "path", "status"],
    )
    HTTP_LATENCY = Histogram(
        "pipe4_http_request_duration_seconds",
        "Pipe 4 request latency",
        ["method", "path"],
    )

    def record_request(method: str, path: str, status: int, duration_s: float) -> None:
        HTTP_REQUESTS.labels(method, path, str(status)).inc()
        HTTP_LATENCY.labels(method, path).observe(duration_s)

    def render_metrics() -> tuple[bytes, str]:
        return generate_latest(), CONTENT_TYPE_LATEST

except Exception:

    def record_request(method: str, path: str, status: int, duration_s: float) -> None:
        return None

    def render_metrics() -> tuple[bytes, str]:
        return (
            b"# prometheus-client unavailable in this environment\n",
            "text/plain; version=0.0.4",
        )
