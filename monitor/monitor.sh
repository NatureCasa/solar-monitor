#!/bin/bash

SCRIPT_PATH="${BASH_SOURCE}"
DIR_NAME=$(dirname "${SCRIPT_PATH}")
echo "DIR: $DIR_NAME"
cd $DIR_NAME
./monitor-loop.sh
