#! /usr/bin/env sh
set -e

/wait-for-it.sh -t 30 "${MYSQL_HOST}:${MYSQL_PORT}"

python ./scripts/ensure-database.py

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
