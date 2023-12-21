#!/bin/sh

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "Postgres did run"

exec "$@"
