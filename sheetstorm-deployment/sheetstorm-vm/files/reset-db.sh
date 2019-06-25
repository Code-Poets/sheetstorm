#! /bin/bash -e

db_name="$1"

psql --host localhost --username postgres <<-EOF
            DROP DATABASE IF EXISTS $db_name;
            CREATE DATABASE $db_name;
EOF
