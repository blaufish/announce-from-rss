#!/bin/bash

set -x
set -e

if [[ ! -d .venv ]]
then
	python3 -m venv .venv
fi

source .venv/bin/activate

if [[ -f requirements.lock ]]
then
	pip3 install -r requirements.lock
	exit
fi

if [[ -f requirements.txt ]]
then
	pip3 install -r requirements.txt
else
	# Generate requirements.txt
	pip3 install -r requirements.in
	pip3 freeze > requirements.txt
fi
deactivate

#
# Generate requirements.lock
#
if which pip-compile
then
	pip-compile --generate-hashes -o requirements.lock requirements.txt
	exit
fi

if [[ ! -d .piptools ]]
then
	python3 -m venv .piptools
fi
source .piptools/bin/activate
python -m pip install pip-tools
pip-compile --generate-hashes -o requirements.lock requirements.txt
