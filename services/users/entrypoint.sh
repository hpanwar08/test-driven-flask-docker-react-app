#!/bin/sh

# if this file is made on windows then convert the eof symbol 
# https://stackoverflow.com/questions/51508150/standard-init-linux-go190-exec-user-process-caused-no-such-file-or-directory
echo "Waiting for postgres..."

while ! nc -z users-db 5432; do
  echo "Waiting for db"
  sleep 0.1
done

echo "PostgreSQL started"

python manage.py run -h 0.0.0.0