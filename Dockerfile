# ---- Builder Stage ----
    FROM python:3.12-slim AS builder

    # 작업 환경 설정
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # 시스템 패키지 설치 (빌드용 - PostgreSQL 클라이언트 빌드에 필요)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        gcc \
        && rm -rf /var/lib/apt/lists/*
    
    # 작업 디렉터리 설정
    WORKDIR /app
    
    # 가상 환경 생성 및 경로 설정
    ENV VIRTUAL_ENV=/opt/venv
    RUN python -m venv $VIRTUAL_ENV
    ENV PATH="$VIRTUAL_ENV/bin:$PATH"
    
    # requirements.txt 복사 및 의존성 설치 (캐시 활용)
    COPY requirements.txt .
    # requirements.txt 에 psycopg가 포함되어 있다고 가정
    RUN pip install --no-cache-dir --upgrade pip \
        && pip install --no-cache-dir -r requirements.txt
    
    # 프로젝트 소스 복사 (의존성 설치 후)
    COPY . .
    
    
    # ---- Runtime Stage ----
    FROM python:3.12-slim AS runtime
    
    # 작업 환경 설정
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    ENV TZ=Asia/Seoul
    
    # 시스템 패키지 설치 (런타임용 - 실제 DB 연결에 필요한 라이브러리)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        tzdata \
        && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # 빌더 스테이지에서 가상 환경 복사
    COPY --from=builder /opt/venv /opt/venv
    
    # 빌더 스테이지에서 애플리케이션 코드 복사
    COPY --from=builder /app /app
    
    # 가상 환경 경로 설정
    ENV PATH="/opt/venv/bin:$PATH"
    
    # (선택 사항, 권장) Non-root user 설정
    # RUN useradd --system --create-home appuser && \
    #     chown -R appuser:appuser /app /opt/venv
    # USER appuser
    
    # 포트 설정
    EXPOSE 8000
    
    # 서버 실행 명령
    # CMD ["gunicorn", "highfive_back.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"] # workers 수는 CPU 코어 수에 맞게 조절
    CMD ["gunicorn", "highfive_back.wsgi:application", "--bind", "0.0.0.0:8000"]