FROM python:3.9.7-alpine3.14

WORKDIR /code

ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PORT=8000
ENV WAIT_FOR_IT_URL https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh

EXPOSE ${PORT}

RUN apk update && \
    apk upgrade && \
    apk add curl gcc musl-dev build-base bash libffi-dev

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /code/

RUN poetry install --no-root --no-dev

# Download wait-for-it.sh
ADD ${WAIT_FOR_IT_URL} /
RUN chmod +x /wait-for-it.sh

COPY ./scripts /code/scripts
COPY ./alembic.ini .
COPY ./alembic ./alembic

COPY ./app /code/app/

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
