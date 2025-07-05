# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY setup_supabase.sql .
COPY .env .

# Expose port for Render (required, even if not used for CLI app)
EXPOSE 10000

CMD ["python", "src/main.py"]