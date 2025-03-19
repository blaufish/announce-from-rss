# RSS to X/Twitter bot

Announces new posts available on the RSS feed to X/Twitter.

Various hard coding and tweaks specific for Säkerhetspodcasten
but may be inspirational to others

## Usage

`./twitter-rss-bot.py -h`

``` plain
usage: twitter-rss-bot.py [-h] --url URL --access-token ACCESS_TOKEN
                          --access-token-secret ACCESS_TOKEN_SECRET
                          --consumer-key CONSUMER_KEY
                          --consumer-secret CONSUMER_SECRET
                          --bearer-token BEARER_TOKEN
                          --secret-type {arg,env,file}
                          [--dry-run | --no-dry-run]
                          [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                          [--days DAYS] [--posts POSTS]
                          [--test-tweet TEST_TWEET]

x/twitter bot

options:
  -h, --help            show this help message and exit
  --url URL             URL to lib-syn RSS feed, e.g. https://sakerhetspodcasten.se/index.xml
  --access-token ACCESS_TOKEN
                        x/twitter secret
  --access-token-secret ACCESS_TOKEN_SECRET
                        x/twitter secret
  --consumer-key CONSUMER_KEY
                        x/twitter secret
  --consumer-secret CONSUMER_SECRET
                        x/twitter secret
  --bearer-token BEARER_TOKEN
                        x/twitter secret
  --secret-type {arg,env,file}
                        secret type/source
  --dry-run, --no-dry-run
                        dry-run inhibits posting
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
  --days DAYS           Maximum days back in RSS history to announce
  --posts POSTS         Maximum posts to emit, avoid spamming
  --test-tweet TEST_TWEET
                        A test tweet, e.g. "hello world testing API"

Hope this help was helpful! :-)
```

Anti-spamming defaults:
* `--dry-run` default to avoid posting when development / testing.
* `--posts POSTS` defaults to `1` to avoid spamming
* `--days DAYS` defaults to `1` to avoid spamming

## Dry-run example

Dry-run will not actually post, but will do every other step.

``` bash
./venv.sh

.venv/bin/python3 twitter-rss-bot.py \
 --url https://blaufish.github.io/feed.xml \
 --access-token secrets/blaush_access_token \
 --access-token-secret secrets/blaufish_access_token_secret \
 --consumer-key secrets/blaufish_consumer_key \
 --consumer-secret secrets/blaufish_consumer_secret \
 --bearer-token secrets/blaufish_bearer_token \
 --secret-type file \
 --days 30 \
 --loglevel DEBUG
```

``` plain
2025-03-13 22:39:15,836 INFO Request feed from https://blaufish.github.io/feed.xml
2025-03-13 22:39:15,969 INFO RSS candidate: Path Length constraint limitations and bypasses
2025-03-13 22:39:15,969 DEBUG RSS skipping old entry: Bluesky RSS announcer
2025-03-13 22:39:15,969 DEBUG RSS skipping old entry: ClassLoader manipulation
2025-03-13 22:39:15,969 DEBUG RSS skipping old entry: Stripes CryptoUtil vulnerability
2025-03-13 22:39:18,186 INFO X/Twitter username: blaufish_
2025-03-13 22:39:18,186 INFO X/Twitter name: @blaufish_
2025-03-13 22:39:18,186 INFO X/Twitter id: 77535685
2025-03-13 22:39:20,665 DEBUG X/Twitter URL https://t.co/heKq5Lf9rr: https://sakerhetspodcasten.se/tags/
2025-03-13 22:39:20,920 DEBUG X/Twitter URL https://t.co/mn7B3PoqCX: https://github.com/blaufish/www-migrate/blob/master/tagger/README.md
2025-03-13 22:39:21,159 DEBUG X/Twitter URL https://t.co/qy9nCu3idW: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_277_ostrukturerat_v_9/
2025-03-13 22:39:21,327 DEBUG X/Twitter URL https://t.co/xHnSmJSPd5: https://blaufish.github.io/security/research/2025/02/15/path-length-constraint.html
2025-03-13 22:39:21,574 DEBUG X/Twitter URL https://t.co/5xdQt9ampo: https://blaufish.github.io/security/research/2025/01/21/classloader-manipluation.html
2025-03-13 22:39:21,818 DEBUG X/Twitter URL https://t.co/wffsIaSD5S: https://www.youtube.com/watch?v=aLoiS6s-DKc
2025-03-13 22:39:22,123 DEBUG X/Twitter URL https://t.co/YdXaMe9y4a: https://www.gov.kz/uploads/2025/2/4/84f9ee83af415a658fc3d2830d317889_original.3875924.pdf
2025-03-13 22:39:22,361 DEBUG X/Twitter URL https://t.co/txP7ofzfqu: https://sakerhetspodcasten.se/posts/sakerhetspodcasten_275_ostukturerat_v_6/
2025-03-13 22:39:22,362 INFO Disregard already published: https://blaufish.github.io/security/research/2025/02/15/path-length-constraint.html
2025-03-13 22:39:22,362 INFO Terminating normally. Thanks for All the Fish!
```
