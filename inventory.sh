#!/bin/bash

pipenv run python -m ssh_config.cli inventory $1 $2
