FROM python:3-alpine

# Disable Python buffering in order to see the logs immediatly
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /workdir

COPY . /workdir

RUN uv sync --frozen --all-extras

CMD tail -f /dev/null
