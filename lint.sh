#!/bin/bash

printf "[FLAKE8: sheetstorm]\n"
flake8                                                                                                      \
    --exclude=sheetstorm-deployment/,sheetstorm/settings/,manage.py,employees/migrations,users/migrations,managers/migrations,     \
    --jobs=4                                                                                                \
    --max-line-length=120                                                                                   \
    --ignore=E124,E126,E128,E131,E156,E201,E221,E222,E241,E265,E271,E272,E701,F405,E501,W503                \
    --per-file-ignores=features/steps/user_initialisation_steps.py:F403,F811
printf "\n"

printf "[PYLINT: sheetstorm]\n"
# Find all subdirectories of our python apps and use xargs to pass them as arguments to pylint

./find-files-to-refactor.sh | xargs pylint --rcfile=pylintrc
printf "\n"
