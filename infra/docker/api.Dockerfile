FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN addgroup --system pipe4 && adduser --system --ingroup pipe4 pipe4

COPY apps/api/pyproject.toml /app/pyproject.toml
COPY apps/api/src /app/src
RUN python -m pip install --no-cache-dir "setuptools>=75" \
    && python -m pip install --no-cache-dir --no-build-isolation .

COPY apps/api/alembic.ini /app/alembic.ini
COPY apps/api/migrations /app/migrations
COPY config /app/config

RUN mkdir -p /var/lib/pipe4/evidence && chown -R pipe4:pipe4 /app /var/lib/pipe4
USER pipe4

EXPOSE 8000
CMD ["uvicorn", "pipe4.app:app", "--host", "0.0.0.0", "--port", "8000"]
