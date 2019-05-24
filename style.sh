#!/bin/bash -e

printf "[ISORT: sheetstorm]\n"
./find-files-to-refactor.sh | xargs isort -sl -l 120
printf "\n"

printf "[BLACK: sheetstorm]\n"
./find-files-to-refactor.sh | xargs black --line-length 120
printf "\n"
