FROM python:3.11-slim

RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

COPY pyproject.toml .
RUN mkdir -p app && touch app/__init__.py && \
    pip install --no-cache-dir . && \
    rm -rf app

COPY . .

EXPOSE 8000
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
