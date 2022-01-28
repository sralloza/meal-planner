#! /usr/bin/env sh
set -e

if [[ -z "${WAIT_FOR_IT_ADDRESS}" ]]; then
  echo "Skipping wait-for-it ($$WAIT_FOR_IT_ADDRESS is not defined)"
else
  echo "running wait-for-it.sh -t 120 ${WAIT_FOR_IT_ADDRESS}"
  /wait-for-it.sh -t 120 "${WAIT_FOR_IT_ADDRESS}"
fi

echo "Ensuring database existence"
python ./scripts/ensure-database.py

echo "Upgrading database"
alembic upgrade head

echo "Launching uvicorn server"
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
