FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

RUN apt-get update && apt-get install -y \
  libx11-6 \
  libxi6 \
  libxxf86vm1 \
  libxcursor1 \
  libxrandr2 \
  libxinerama1 \
  libglib2.0-0 \
  libsm6 \
  libice6 \
  libglu1-mesa \
  libgl1 \
  libxkbcommon0 \
  libegl-mesa0 \
  libglvnd-dev

RUN uv sync --python=/usr/local/bin/python3.11

CMD uv run main.py
