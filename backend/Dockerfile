FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create static directory for audio files
RUN mkdir -p /app/static/audio

# Generate Prisma client
RUN prisma generate

# entrypoint.sh 스크립트를 복사하고 실행 권한을 부여합니다.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# 컨테이너 시작 시 entrypoint.sh를 실행하도록 설정합니다.
ENTRYPOINT ["/app/entrypoint.sh"]

# Run migrations and start server
# 이 명령어는 entrypoint.sh의 `exec "$@"` 부분으로 전달됩니다.
CMD ["sh", "-c", "prisma migrate deploy && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
