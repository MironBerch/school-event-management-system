#!/bin/sh

while ! nc -z db 5432; do
  sleep 0.1
done

echo "Postgres did run"

exec "$@"
