#!/usr/bin/env bash

docker-compose -f docker-compose-local.yml pull --parallel;
docker-compose -f docker-compose-local.yml up --build;
