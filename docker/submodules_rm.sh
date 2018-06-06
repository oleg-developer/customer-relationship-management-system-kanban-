#!/usr/bin/env bash

git submodule deinit -f -- niceerp-front
rm -rf ../.git/modules/docker/niceerp-front
git rm -f niceerp-front

git submodule deinit -f -- rasa-board-server
rm -rf ../.git/modules/docker/rasa-board-server
git rm -f rasa-board-server