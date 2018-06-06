#!/usr/bin/env bash

git submodule update --recursive --remote --force;
docker-compose -f docker-compose-dev.yml pull --parallel;
docker-compose -f docker-compose-dev.yml up --build -d;
