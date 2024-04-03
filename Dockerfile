FROM python:3.12.2-slim as builder

ENV POETRY_VERSION=1.8.0
ENV POETRY_HOME=/opt/poetry
ENV PATH="/root/.local/bin:${PATH}"

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx
RUN pipx install poetry==$POETRY_VERSION

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root

RUN pipx uninstall poetry


FROM python:3.12.2-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /app/.venv /venv
COPY app ./app
COPY alembic.ini ./
COPY migrations ./migrations
COPY .env ./
COPY docker-entrypoint.sh ./

RUN chmod u+x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

