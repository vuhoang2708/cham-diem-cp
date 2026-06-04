FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt requirements-cloud.txt ./
RUN pip install --no-cache-dir -r requirements-cloud.txt

# App code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY data/ ./data/

# Ensure data dir writable
RUN mkdir -p /app/data

ENV DATA_SOURCE=cloud
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
