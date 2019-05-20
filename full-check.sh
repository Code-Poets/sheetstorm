#!/usr/bin/env bash
printf "=================== DJANGO CONFIGURATION CHECKS ====================\n"
python manage.py check
printf "\n"

printf "=========================== CODING STYLE ===========================\n"
./style.sh
printf "\n"

printf "=============================== LINT ===============================\n"
./lint.sh
printf "\n"

printf "========================= MYPY STATIC TYPE CHECKER =================\n"
mypy --config-file=mypy.ini .
printf "\n"

printf "========================= UNIT TESTS WITH COVERAGE =================\n"
# NOTE: 'manage.py test' does not find all tests unless we run it from within the app directory.
./run-test-coverage.sh
printf "\n"
