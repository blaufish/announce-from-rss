# RSS to Bluesky bot

Announces new posts available on the RSS feed to Bluesky.

Various hard coding and tweaks specific for Säkerhetspodcasten
but may be inspirational to others

## Usage

`./bsky-rss-bot.py -h`

``` plain
usage: bsky-rss-bot.py [-h] --url URL --handle HANDLE --secret SECRET --secret-type {arg,env,file} [--dry-run | --no-dry-run] [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--days DAYS] [--posts POSTS]

bluesky bot

options:
  -h, --help            show this help message and exit
  --url URL             URL to lib-syn RSS feed, e.g. https://sakerhetspodcasten.se/index.xml
  --handle HANDLE       bluesky handle
  --secret SECRET       bluesky secret
  --secret-type {arg,env,file}
                        bluesky secret type
  --dry-run, --no-dry-run
                        dry-run inhibits posting (default: True)
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
  --days DAYS           Maximum days back in RSS history to announce
  --posts POSTS         Maximum posts to emit, avoid spamming

Hope this help was helpful! :-)
```

Anti-spamming defaults:
* `--dry-run` default to avoid posting when development / testing.
* `--posts POSTS` defaults to `1` to avoid spamming
* `--days DAYS` defaults to `1` to avoid spamming

## Dry-run example

Dry-run will not actually post, but will do every other step.

``` bash
./bsky-rss-bot.py \
   --url https://sakerhetspodcasten.se/index.xml \
   --handle blaufish.bsky.social \
   --days 60 \
   --dry-run \
   --secret .bluesky2.secret \
   --secret-type file
```

``` plain
2025-02-04 10:53:03,238 INFO Request feed from https://sakerhetspodcasten.se/index.xml
2025-02-04 10:53:03,277 INFO RSS candidate: Säkerhetspodcasten #275 - Ostukturerat V.6
2025-02-04 10:53:03,277 INFO RSS candidate: Säkerhetspodcasten #274 - Fyra fantastiska frågor
2025-02-04 10:53:03,277 INFO RSS candidate: Säkerhetspodcasten #273 - Ostrukturerat V.50
2025-02-04 10:53:03,607 INFO Bluesky lookup: blaufish.bsky.social=did:plc:y25e3xvbgsjuqcxjdybktovi
2025-02-04 10:53:04,886 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_275_ostukturerat_v_6/
2025-02-04 10:53:04,886 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_274_fyra_fantastiska_fragor/
2025-02-04 10:53:04,886 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_273_ostrukturerat_v_50/
2025-02-04 10:53:04,886 INFO Terminating normally. Thanks for All the Fish!
```

## Posting example

``` bash
./bsky-rss-bot.py \
   --url https://sakerhetspodcasten.se/index.xml \
   --handle blaufish.bsky.social \
   --days 60 \
   --no-dry-run \
   --secret .bluesky2.secret \
   --secret-type file
```

``` plain
2025-02-04 10:53:07,035 INFO Request feed from https://sakerhetspodcasten.se/index.xml
2025-02-04 10:53:07,065 INFO RSS candidate: Säkerhetspodcasten #275 - Ostukturerat V.6
2025-02-04 10:53:07,065 INFO RSS candidate: Säkerhetspodcasten #274 - Fyra fantastiska frågor
2025-02-04 10:53:07,065 INFO RSS candidate: Säkerhetspodcasten #273 - Ostrukturerat V.50
2025-02-04 10:53:07,384 INFO Bluesky lookup: blaufish.bsky.social=did:plc:y25e3xvbgsjuqcxjdybktovi
2025-02-04 10:53:08,567 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_275_ostukturerat_v_6/
2025-02-04 10:53:08,567 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_274_fyra_fantastiska_fragor/
2025-02-04 10:53:08,567 INFO Disregard already published: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_273_ostrukturerat_v_50/
2025-02-04 10:53:08,567 INFO Terminating normally. Thanks for All the Fish!
```
