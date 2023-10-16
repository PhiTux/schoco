#!/bin/bash

mkdir -p ./data/containers
mkdir -p ./data/projects

# call alembic upgrades
alembic -c alembic_prod.ini upgrade head
