#!/bin/bash -e

find . -type f                              \
    -not -path "./sheetstorm/settings/*"    \
    -not -path "*/migrations/*"             \
    -name "*.py"                     \
