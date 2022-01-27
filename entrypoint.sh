#! /usr/bin/env sh
set -e

if [[ -z "${WAIT_FOR_IT_ADDRESS}" ]]; then
/wait-for-it.sh -t 30 "${WAIT_FOR_IT_ADDRESS}"
fi

python ./scripts/ensure-database.py

alembic upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
