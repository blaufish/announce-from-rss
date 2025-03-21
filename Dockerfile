ARG REQUIREMENT_TXT="keep"

FROM ubuntu:noble

RUN \
 apt update -y && \
 apt install python3 -y && \
 apt install python3.12-venv -y

COPY \
 implementation_bsky.py \
 implementation_mastodon.py \
 implementation_twitter.py \
 requirements.in \
 requirements.lock \
 requirements.txt \
 rss-bot.py \
 utils.py \
 venv.sh \
 /build/

RUN test "$REQUIREMENT_TXT" = "refresh" ||\
 rm /build/requirements.txt\
 /build/requirements.lock

RUN cd /build/ && \
  bash -c "source venv.sh" && \
  .venv/bin/python3 rss-bot.py -h
