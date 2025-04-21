# 1단계: PDM 설치 & 의존성 캐시 분리
FROM python:3.9.21 AS pdm-stage

WORKDIR /app

# 시스템 필수 패키지 + PDM 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 ffmpeg git && \
    pip install pdm && \
    apt-get clean

# 의존성 파일만 먼저 복사
COPY pyproject.toml pdm.lock ./

# 의존성 설치 (캐시 사용됨)
RUN pdm install

# 전체 프로젝트 복사
COPY . .


#  2단계: 최종 런타임 이미지
FROM python:3.9.21

WORKDIR /app

# 최소 시스템 패키지 + PDM만 재설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    pip install pdm && \
    apt-get clean

# 빌드 단계 결과 복사
COPY --from=pdm-stage /app /app

#  자동 실행: pdm run main.py
CMD ["pdm", "run", "python", "main.py"]























#FROM python:3.9.21

# 시스템 패키지 설치: OpenCV에 필요한 라이브러리
#RUN apt-get update && apt-get install -y \
    #libgl1-mesa-glx libglib2.0-0 ffmpeg git && \
    #pip install pdm && \
    #apt-get clean

# 작업 디렉토리 설정
#WORKDIR /app

# 프로젝트 복사 (main.py, pyproject.toml 등)
#COPY . .

# 의존성 설치 (pdm.lock이 있으면 lock 기준, 없으면 pyproject.toml 기준)
#RUN pdm install

# 실행 명령어
#CMD ["pdm", "run", "python", "main.py"]
