#!/bin/bash

set -x
set -e
version="0.0.1"
tag=$(git tag -l -- "v$version")

git fetch --tags

if [ "$tag" != "" ]
then
    echo "Version $version allready exists."
    exit 1
fi

./build.sh release

porcelain="$(git status --porcelain=v2)"

if [ "$porcelain" ]
then
	echo "Directory is not clean. Exiting!"
	exit 1
fi

git tag -a "v$version" -m "Release version $version"
