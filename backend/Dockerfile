# ---- Base image ----
FROM python:3.11-slim AS base

# ---- Environment setup ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5185 \
    HOST=0.0.0.0

# ---- Install system dependencies ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- App setup ----
WORKDIR /app

# ---- Install dependencies ----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Copy app source ----
COPY . .

# ---- Expose port ----
EXPOSE 5185

# ---- Run the app ----
CMD ["python", "app.py"]

# ---- Labels for GHCR ----
ARG GITHUB_REPOSITORY
ARG IMAGE_VERSION

LABEL org.opencontainers.image.title="dataviz-constructor"
LABEL org.opencontainers.image.description="Проект датавиз-конструктор предназначен для обработки и анализа данных через визуализацию. Итогом работы является дашборд или вычислительное эссе."
LABEL org.opencontainers.image.source="https://github.com/${GITHUB_REPOSITORY}"
LABEL org.opencontainers.image.version="${IMAGE_VERSION}"
