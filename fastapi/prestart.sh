#!/bin/bash

mkdir -p ./data/containers
mkdir -p ./data/projects

# call alembic upgrades iff /app/data/sql_app.db exists
if [ -f /app/data/sql_app.db ]; then
    alembic -c alembic_prod.ini upgrade head
fi
