#!/usr/bin/env bash

pytest --cov=$(dirname $0)/../tiny/  --cov-fail-under=90 -W ignore::DeprecationWarning
