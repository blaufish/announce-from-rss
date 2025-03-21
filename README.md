# RSS to Socials announcer

Announce your RSS entries to social media networks:
**Mastodon**, **Bluesky**, **X** (**Twitter**).

## Usage

`./rss-bot.py -h`:

``` plain
usage: rss-bot.py [-h] --config CONFIG

rss announcer bot

options:
  -h, --help       show this help message and exit
  --config CONFIG  Configuration file location

Hope this help was helpful! :-)
```

An example configuration file is provided:
* [example.yaml](example.yaml)

Example: `./rss-bot.py --config example.yaml`

``` plain
2025-03-21 15:00:31,034 INFO Dryrun: announcements are inhibited.
2025-03-21 15:00:31,034 INFO Limit: max announcements: 1.
2025-03-21 15:00:31,034 INFO Limit: max days: 3.
2025-03-21 15:00:31,034 INFO Request feed from: https://example.com/feed.xml
2025-03-21 15:00:31,720 INFO No new RSS entries within the last 3 day(s), exiting!
```

Example: `./rss-bot.py --config local-blaufish.yaml`

``` plain
2025-03-21 15:02:04,331 INFO Dryrun: announcements are inhibited.
2025-03-21 15:02:04,331 INFO Limit: max announcements: 1.
2025-03-21 15:02:04,331 INFO Limit: max days: 3.
2025-03-21 15:02:04,331 INFO Request feed from: https://blaufish.github.io/feed.xml
2025-03-21 15:02:04,661 INFO RSS candidate: Git Octopus Merge with Unrelated histories
2025-03-21 15:02:04,661 INFO Bot implementation twitter is disabled.
2025-03-21 15:02:04,661 INFO Mastodon bot implementation: startup
2025-03-21 15:02:04,911 INFO Mastodon id: 114143993986981521
2025-03-21 15:02:04,911 INFO Mastodon username: blaufish
2025-03-21 15:02:04,911 INFO Mastodon acct: blaufish
2025-03-21 15:02:04,911 INFO Mastodon display name: blaufish
2025-03-21 15:02:05,131 INFO Disregard already published: https://blaufish.github.io/development/2025/03/19/git-octopus-with-unrelated-histories.html
2025-03-21 15:02:05,132 INFO Bluesky bot implementation: startup
2025-03-21 15:02:05,544 INFO Bluesky lookup: blaufish.bsky.social=did:plc:y25e3xvbgsjuqcxjdybktovi
2025-03-21 15:02:06,808 INFO Disregard already published: https://blaufish.github.io/development/2025/03/19/git-octopus-with-unrelated-histories.html
2025-03-21 15:02:06,809 INFO Terminating normally. Thanks for All the Fish!
```

## RSS Configuration

``` yaml
url: https://example.com/feed.xml
transformer: sakerhetspodcasten
```

`url` is the RSS channel source URL. 

`transformer` is RSS entry preprocessors.
Leave empty or comment out unless there is a transformer implemented for you.

## Logging configuration

``` yaml
loglevel: DEBUG
```

Supported values are:
 `DEBUG`, 
 `INFO`,
 `WARNING`,
 `ERROR`,
 `CRITICAL`.

Default if commented out is `INFO`.

Logging is backed by Python Logging framework; \
[Logging HOWTO](https://docs.python.org/3/howto/logging.html)

## Limits configuration

``` yaml
limits:
  days: 3
  posts: 1
  dryrun: true
```

`days`: how old posts will be announced. Default is 1.

`posts` maximum number of posts to announce. Default is 1.

`dryrun`: inhibit posting, just test that configuration is OK.

* Default is **true**.
* Set to **false** to actually start posting.

## Secrets configuration

``` yaml
secret_type: env
```

`secret_type`: where to obtain secrets from.
 
* `plain`: secrets are written directly in configuration file.
* `env`: secrets are obtain from environment variable by reference.
* `file`: secrets are obtained from file by reference.


`env` by reference example:

``` yaml
secret_type: env
mastodon:
  secrets:
    access_token: M_ACCESS_TOKEN
```

would obtain `mastodon.secrets.access_token` from `ENV[M_ACCESS_TOKEN]`.

`file`by reference example:

``` yaml
secret_type: env
mastodon:
  secrets:
    access_token: m_access_token.secret.txt
```

would obtain `mastodon.secrets.access_token` from file `m_access_token.secret.txt`.

## Genetic implementation configurations

Any implementation will be disabled if:

* No configuration entry.
* Empty configuration, e.g. `mastodon:` with no more configuration.
* Disabled configuration.

You disable an configuration with `enabled: false`.

``` yaml
mastodon:
  enabled: false
  secrets:
    access_token: M_ACCESS_TOKEN
```

Disabling a configuration allows you to keep the configuration to
remain while inactive.
Useful for example if there is a temporary reason to not interact
with a service.

## Mastodon configuration

``` yaml
mastodon:
  secrets:
    access_token: M_ACCESS_TOKEN
    api_base_uri: https://mastodon.social
```

`access_token`: application access token from developer settings.

`api_base_uri`: mastodon API server. 
Defaults to `https://mastodon.social`.

## Bluesky configuration

``` yaml
bsky:
  handle: example.bsky.social
  secrets:
    password: BLUESKY_APP_PASSWORD
```

Bluesky needs an application access token from developer settings.

## Twitter configuration

``` yaml
twitter:
  secrets:
    access_token: X_ACCESS_TOKEN
    access_token_secret: X_ACCESS_TOKEN_SECRET
    bearer_token: X_BEARER_TOKEN
    client_id: X_CLIENT_ID
    client_secret: X_CLIENT_SECRET
    consumer_key: X_CONSUMER_KEY
    consumer_secret: X_CONSUMER_SECRET
```
