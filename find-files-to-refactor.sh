#!/bin/bash -e

find . -type f                              \
    -not -path "./sheetstorm/settings/*"    \
    -not -path "*/migrations/*"             \
    -not -path "*/sheetstorm-deployment/*"  \
    -name "*.py"                            \
