#!/bin/bash

printf "[FLAKE8: time-monkey]\n"
flake8                                                                          \
    --exclude=settings, manage.py, \
    --jobs=4                                                                    \
    --ignore=E124,E126,E128,E131,E156,E201,E221,E222,E225,E241,E251,E265,E271,E272,E501,E701,F405
printf "\n"

printf "[PYLINT: time-monkey]\n"
# Find all subdirectories of our python apps and use xargs to pass them as arguments to pylint

find time_monkey/ -maxdepth 1 -mindepth 1 -type d \
    | xargs pylint --rcfile=pylintrc
printf "\n"
