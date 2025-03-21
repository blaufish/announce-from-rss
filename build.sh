#!/bin/sh

set -e
set -x

REQUIREMENT_TXT=keep
RELEASE_SUFFIX=""
if [ "$1" = "release" ]
then
	REQUIREMENT_TXT=refresh
	RELEASE_SUFFIX="-release"
fi

TAG="$(git describe --long --dirty)${RELEASE_SUFFIX}"
IMAGE=localhost/announce-from-rss
IMAGE_TAG="$IMAGE:$TAG"
OUTDIR="$PWD/out"

podman build \
	--build-arg REQUIREMENT_TXT="$REQUIREMENT_TXT" \
	-t "$IMAGE_TAG" \
	.

if [ "$REQUIREMENT_TXT" = "refresh" ]
then
	mkdir -p -- "$OUTDIR"

	podman run --rm -v "$OUTDIR":/out:rw "$IMAGE_TAG" \
		cp /build/requirements.txt /out/requirements.txt
	podman run --rm -v "$OUTDIR":/out:rw "$IMAGE_TAG" \
		cp /build/requirements.lock /out/requirements.lock

	cp -- "$OUTDIR/requirements.txt" requirements.txt
	cp -- "$OUTDIR/requirements.lock" requirements.lock
fi
