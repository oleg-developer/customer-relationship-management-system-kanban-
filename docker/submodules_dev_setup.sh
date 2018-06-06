#!/usr/bin/env bash

git submodule add -b test http://gitlab.nicecode.biz:8070/kirbaba.v/niceerp-front.git niceerp-front-dev
git submodule add -b test http://gitlab.nicecode.biz:8070/kvn/rasa-board-server.git rasa-board-server-dev
git submodule update --init

git submodule update --recursive --remote --force