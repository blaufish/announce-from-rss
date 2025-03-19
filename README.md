# RSS to Mastodon bot

Announces new posts available on the RSS feed to Mastodon

Various hard coding and tweaks specific for Säkerhetspodcasten
but may be inspirational to others

## Usage

`./mastodon-rss-bot.py -h`

``` plain
./mastodon-rss-bot.py -h
usage: mastodon-rss-bot.py [-h]
                           --url URL
                           --access-token ACCESS_TOKEN
                           --secret-type {arg,env,file}
                           [--api-base-url API_BASE_URL]
                           [--dry-run | --no-dry-run]
                           [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                           [--days DAYS] [--posts POSTS]
                           [--test-toot TEST_TOOT]

mastodon bot

options:
  -h, --help            show this help message and exit
  --url URL             URL to lib-syn RSS feed, e.g.
                        https://sakerhetspodcasten.se/index.xml
  --access-token ACCESS_TOKEN
                        "Your access token" in application settings
  --secret-type {arg,env,file}
                        secret type/source
  --api-base-url API_BASE_URL
                        Default https://mastodon.social
  --dry-run, --no-dry-run
                        dry-run inhibits posting
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
  --days DAYS           Maximum days back in RSS history to announce
  --posts POSTS         Maximum posts to emit, avoid spamming
  --test-toot TEST_TOOT
                        A test toot, e.g. "hello world testing API"

Hope this help was helpful! :-)
```

Anti-spamming defaults:
* `--dry-run` default to avoid posting when development / testing.
* `--posts POSTS` defaults to `1` to avoid spamming
* `--days DAYS` defaults to `1` to avoid spamming

## Example usage

Dry-run will not actually post, but will do every other step.

``` bash
./venv.sh

.venv/bin/python3 mastodon-rss-bot.py \
 --url https://blaufish.github.io/feed.xml \
 --access-token secrets/access_token \
 --secret-type file \
 --days 10 \
 --loglevel DEBUG
```

``` plain
2025-03-18 15:53:38,837 INFO Request feed from https://blaufish.github.io/feed.xml
2025-03-18 15:53:39,124 INFO RSS candidate: X/Twitter RSS announcer
2025-03-18 15:53:39,125 DEBUG RSS skipping old entry: Path Length constraint limitations and bypasses
2025-03-18 15:53:39,125 DEBUG RSS skipping old entry: Bluesky RSS announcer
2025-03-18 15:53:39,125 DEBUG RSS skipping old entry: ClassLoader manipulation
2025-03-18 15:53:39,125 DEBUG RSS skipping old entry: Stripes CryptoUtil vulnerability
2025-03-18 15:53:39,314 INFO Mastodon id: 114143993986981521
2025-03-18 15:53:39,314 INFO Mastodon username: blaufish
2025-03-18 15:53:39,314 INFO Mastodon acct: blaufish
2025-03-18 15:53:39,314 INFO Mastodon display name: blaufish
2025-03-18 15:53:39,581 INFO Disregard already published: https://blaufish.github.io/development/2025/03/14/x-twitter-rss.html
2025-03-18 15:53:39,581 INFO Terminating normally. Thanks for All the Fish!
```
