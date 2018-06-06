#!/usr/bin/env bash

git submodule deinit -f -- niceerp-front-dev
rm -rf ../.git/modules/docker/niceerp-front-dev
git rm -f niceerp-front-dev

git submodule deinit -f -- rasa-board-server-dev
rm -rf ../.git/modules/docker/rasa-board-server-dev
git rm -f rasa-board-server-dev