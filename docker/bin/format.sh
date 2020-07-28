#!/bin/sh

cd /app

echo "Running black..."
black --config /app/pyproject.toml /app/
echo

echo "Running isort..."
isort -y
echo
