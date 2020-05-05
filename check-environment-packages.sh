#!/bin/bash -e

if [[ -z "$VIRTUAL_ENV" ]]
then
    RED_COLOR='\033[0;31m'
    GREEN_COLOR='\033[0;32m'
    NO_COLOR='\033[0m'
    printf "${RED_COLOR}Script must be run with activated virtualenv!\n${NO_COLOR}You can activate shell by: ${GREEN_COLOR}pipenv shell\n"
    exit 1
fi

pipenv uninstall --all

pipenv install --dev --clear

