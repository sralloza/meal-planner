FROM python:3.10.9-slim-bullseye as base

RUN apt update && apt upgrade -y && \
    apt install jq curl -y

FROM base as builder

WORKDIR /app

RUN apt install build-essential libssl-dev libffi-dev python3-dev cargo -y

RUN curl -sSL https://install.python-poetry.org | python - && \
    cd /usr/local/bin && \
    ln -s /root/.local/bin/poetry

ENV POETRY_VIRTUALENVS_CREATE false

RUN pip install virtualenv && \
    virtualenv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main --no-root

COPY ./app ./app
RUN poetry install --only main

FROM base

WORKDIR /app

COPY --from=builder /app/pyproject.toml /app/poetry.lock /app/README.md ./
COPY alembic/ /app/alembic
COPY alembic.ini /app/
COPY --from=builder /app/app ./app
COPY --from=builder /app/.venv ./.venv
COPY ./delivery /delivery
COPY ./scripts /scripts

RUN chmod +x /delivery/*.sh

EXPOSE 8080

ENV IS_PRODUCTION=true
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "/delivery/entrypoint.sh" ]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
