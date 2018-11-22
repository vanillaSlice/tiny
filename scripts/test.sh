#!/usr/bin/env bash

python -W ignore::DeprecationWarning -m unittest discover $(dirname $0)/../tests
