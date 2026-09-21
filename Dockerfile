# Dockerfile for Real Estate Insights (Backend + Frontend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy repository content
COPY backend /app/backend
COPY data /app/data
COPY docs /app/docs

WORKDIR /app/backend

EXPOSE 8000

CMD ["gunicorn", "realestate_chatbot.wsgi:application", "--bind", "0.0.0.0:8000"]

