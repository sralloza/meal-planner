#! /usr/bin/env sh
set -e

python ./scripts/ensure-database.py

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
