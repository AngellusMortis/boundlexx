#!/bin/sh

cd /app

echo "Running black..."
black . --check
exit_code=$?
echo

echo "Running flake8..."
flake8 .
test $? -eq 0 -a $exit_code -eq 0
exit_code=$?
echo

echo "Running pylint..."
pylint boundlexx tests
test $? -eq 0 -a $exit_code -eq 0
exit_code=$?
echo

echo "Running isort..."
isort -c
test $? -eq 0 -a $exit_code -eq 0
exit_code=$?
echo

echo "Running mypy..."
mypy .
test $? -eq 0 -a $exit_code -eq 0
exit_code=$?
echo

echo "Running bandit..."
bandit .
test $? -eq 0 -a $exit_code -eq 0
exit_code=$?
echo

exit $exit_code
