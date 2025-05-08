# 베이스 이미지 선택

FROM python:3.12

# 필수 시스템 패키지 설치 (mysqlclient 빌드에 필요)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉터리 설정
WORKDIR .

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --verbose -r requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir --upgrade pip mysqlclient==2.2.0
# 프로젝트 소스 복사
COPY . .

# 포트 설정
EXPOSE 8000

# 서버 실행 명령
CMD ["gunicorn", "highfive_back.wsgi:application", "--bind", "0.0.0.0:8000"]