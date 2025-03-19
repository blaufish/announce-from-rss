#!/bin/bash

set -x
set -e


if [[ ! -d .venv ]]
then
	# sudo apt install python3.10-venv
	python3 -m venv .venv
fi

source .venv/bin/activate

if [[ -f requirements.txt ]]
then
	pip3 install -r requirements.txt
else
	pip3 install -r requirements.in
	pip3 freeze > requirements.txt
fi
