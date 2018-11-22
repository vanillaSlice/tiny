#!/usr/bin/env bash

pytest --cov=$(dirname $0)/../tiny/ -W ignore::DeprecationWarning
