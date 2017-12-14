#!/bin/bash -e

cd "$(dirname $0)"

PYTHONPATH=.. python3 -m pytest "$@"
