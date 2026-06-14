# front/Dockerfile (Streamlit 프론트 이미지)
FROM python:3.12-slim

WORKDIR /app

# 의존성 먼저 설치 (레이어 캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

EXPOSE 8501

# Streamlit 실행 (외부 접속 위해 0.0.0.0, WebSocket 재연결 방지로 CORS/XSRF 비활성화.....)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
