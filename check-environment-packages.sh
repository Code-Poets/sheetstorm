#!/bin/bash

pipenv --rm

yes | pipenv install --dev --clear --three

pipenv check

if [[ -z "$VIRTUAL_ENV" ]]
then
      pipenv shell
fi
