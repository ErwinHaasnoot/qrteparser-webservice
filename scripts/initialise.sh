#!/bin/bash
echo "Removing existing migrations."
find */migrations/* | grep -v __init__.py | xargs rm

echo "rebuilding migrations"
./manage.py makemigrations

echo "Delete db"
rm db.sqlite3

echo "migrate"
./manage.py migrate
