FROM python:3.9.21

# 시스템 패키지 설치: OpenCV에 필요한 라이브러리
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 ffmpeg git && \
    pip install pdm && \
    apt-get clean

# 작업 디렉토리 설정
WORKDIR /app

# 프로젝트 복사 (main.py, pyproject.toml 등)
COPY . .

# 의존성 설치 (pdm.lock이 있으면 lock 기준, 없으면 pyproject.toml 기준)
RUN pdm install

# 실행 명령어
CMD ["pdm", "run", "python", "main.py"]
