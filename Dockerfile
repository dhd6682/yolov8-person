FROM python:3.9.21 AS pdm-stage

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 ffmpeg git && \
    pip install pdm && \
    apt-get clean

COPY pyproject.toml pdm.lock README.md ./
RUN pdm install
COPY . .

FROM python:3.9.21

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 ffmpeg && \
    pip install pdm && \
    apt-get clean

COPY --from=pdm-stage /app /app

CMD ["pdm", "run", "python", "main.py"]
