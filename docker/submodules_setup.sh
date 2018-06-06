#!/usr/bin/env bash

git submodule add http://gitlab.nicecode.biz:8070/kirbaba.v/niceerp-front.git
git submodule add http://gitlab.nicecode.biz:8070/kvn/rasa-board-server.git
git submodule update --init

git submodule update --recursive --remote --force