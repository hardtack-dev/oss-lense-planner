# back/Dockerfile (FastAPI 백엔드 이미지)
FROM python:3.12-slim

# print 로그가 버퍼링 없이 바로 docker logs에 찍히도록 (데모 로그 시연용)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 설치 (레이어 캐시 활용!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

EXPOSE 8000

# uvicorn 외부 접속 위해 0.0.0.0
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
