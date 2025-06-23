FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install . && \
    pip install httpx mypy pre-commit pytest pytest-asyncio ruff

EXPOSE 80

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]
