FROM python:3.11-slim

WORKDIR /app
COPY backend-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend-api/ . 