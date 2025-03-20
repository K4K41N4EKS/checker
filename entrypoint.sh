#!/bin/bash
echo "Ожидание PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done
echo "PostgreSQL запущен!"

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload