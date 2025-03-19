#!.venv/bin/python3

import argparse
from datetime import datetime, timedelta
import feedparser
import html
import logging
import os
import re
import requests
import time
import tweepy

#
# Global variables, arguments
#

threshold = None
logger = None


def logging_setup(level):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    FORMAT = '%(asctime)s %(levelname)-s %(message)s'
    logging.basicConfig(format = FORMAT)

#
# Utility functions
#

def process_rss(url):
    candidates = []
    logger.info(f"Request feed from {url}")
    rss = feedparser.parse(url)
    entries = rss['entries'];
    for entry in entries:
        candidate = process_entry(entry)
        if (candidate):
            candidates.append(entry)
    return candidates

def process_entry(e):
    link             = e['link']
    published_parsed = e['published_parsed']
    published        = e['published']
    title            = e['title']

    ts = time.mktime( published_parsed )
    dt = datetime.fromtimestamp(ts)

    if dt > threshold:
        logger.info(f"RSS candidate: {title}")
        return True
    else:
        logger.debug(f"RSS skipping old entry: {title}")
        return False

def read_secret(secret_argument, secret_type):
    if secret_argument == '-':
        return None
    secret = None
    match secret_type:
        case "arg":
            content = secret_argument
            secret = content.strip()
        case "env":
            content = os.environ[secret_argument]
            secret = content.strip()
        case "file":
            with open(secret_argument, "r") as f:
                content = f.read();
                secret = content.strip()
        case "_":
            logger.error(f"TODO implement! Unknown secret_type: {secret_type}")
            return
    return secret

def xtwitter_decode_url(url):
    if url.startswith('http://t.co/'):
        pass
    elif url.startswith('https://t.co/'):
        pass
    else:
        return url
    r = requests.get(url, allow_redirects=False)
    if 'Location' not in r.headers:
        return url
    decoded_url = r.headers['Location']
    return decoded_url

def xtwitter_list_posted_urls(api2, user_id):
    posts = None
    time.sleep(2) # 429 Too Many Requests
    try:
        posts = api2.get_users_tweets(id = user_id)
    except Exception as e:
        logger.error(f"api2.get_users_tweets(...): {e}")
        return None
    urls = []
    for post in posts.data:
        #time.sleep(2) # 429 Too Many Requests
        strpost = str(post)
        words = strpost.split()
        for word in words:
            if word.startswith('https://'):
                pass
            elif word.startswith('http://'):
                pass
            else:
                continue
            if word in urls:
                continue
            urls.append(word)
    return urls

def xtwitter_decode_urls(urls):
    urls2 = []
    for url in urls:
        decoded_url = xtwitter_decode_url(url)
        if decoded_url in urls2:
            continue
        urls2.append(decoded_url)
        logger.debug(f'X/Twitter URL {url}: {decoded_url}')
    return urls2

def xtwitter_post_raw(api2, text):
    time.sleep(2)
    out = api2.create_tweet(text=text)
    logger.info(f"Tweet errors: {out.errors}")
    logger.info(f"Tweet id: {out.data['id']}")
    logger.info(f"Tweet text: {out.data['text']}")

def xtwitter_post(api2, candidate, dryrun):
    c_title = candidate.title
    c_description = candidate.description

    # Not needed with X/Twitter?
    # Convert entities, e.g. &amp; to &
    #c_description = html.unescape( c_description )

    c_desc = re.sub(r"Lyssna mp3, längd: ", "", c_description)
    c_desc = re.sub(r" Innehåll ", " ", c_desc)
    c_uri = candidate.link
    logger.debug(f"c_title: {c_title}")
    logger.debug(f"c_description: {c_description}")
    logger.debug(f"c_desc: {c_desc}")
    logger.debug(f"c_uri: {c_uri}")

    text = "📣 " + c_title + " 📣 " + c_desc

    c_uri_len = len(c_uri)
    if c_uri_len > 200:
        logger.error(f'Insanely long URI causing error: {c_uri}')
        return

    truncated_len = 240 - 1 - c_uri_len
    text_truncate = truncate( text, truncated_len )
    text_final = text_truncate + '\n' + c_uri

    if dryrun:
        logger.info(f"Dry-run post: {c_uri}")
    else:
        logger.info(f"Post: {c_uri}")
        xtwitter_post_raw(api2, text_final)

def truncate( text, maxlen ):
    if len(text) < maxlen:
        return text
    idx = text.rfind(" ", 0, maxlen-3)
    return text[:idx] + "..."

def main():
    global threshold

    parser = argparse.ArgumentParser(
            prog = 'twitter-rss-bot.py',
            description = 'x/twitter bot',
            epilog = 'Hope this help was helpful! :-)')
    #
    # Required arguments
    #
    parser.add_argument('--url',
            dest = 'url',
            required = True,
            help = 'URL to lib-syn RSS feed, e.g. https://sakerhetspodcasten.se/index.xml')
    parser.add_argument('--access-token',
            dest = 'access_token',
            required = True,
            help = 'x/twitter secret')
    parser.add_argument('--access-token-secret',
            dest = 'access_token_secret',
            required = True,
            help = 'x/twitter secret')
    parser.add_argument('--consumer-key',
            dest = 'consumer_key',
            required = True,
            help = 'x/twitter secret')
    parser.add_argument('--consumer-secret',
            dest = 'consumer_secret',
            required = True,
            help = 'x/twitter secret')
    parser.add_argument('--bearer-token',
            dest = 'bearer_token',
            required = True,
            help = 'x/twitter secret')
    parser.add_argument('--secret-type',
            dest = 'secret_type',
            required = True,
            choices = ['arg', 'env', 'file'],
            help = 'secret type/source')
    #
    # Optional arguments
    #
    parser.add_argument('--dry-run',
            dest = 'dryrun',
            default = True,
            action = argparse.BooleanOptionalAction,
            help = 'dry-run inhibits posting')
    parser.add_argument('--loglevel',
            dest = 'loglevel',
            default = 'INFO',
            choices = ['DEBUG','INFO','WARNING','ERROR','CRITICAL'])
    parser.add_argument('--days',
            dest = 'days',
            type=int,
            default = 1,
            help = 'Maximum days back in RSS history to announce')
    parser.add_argument('--posts',
            dest = 'posts',
            type=int,
            default = 1,
            help = 'Maximum posts to emit, avoid spamming')
    parser.add_argument('--test-tweet',
            dest = 'test_tweet',
            default = None,
            help = 'A test tweet, e.g. "hello world testing API"')

    # prase
    args = parser.parse_args()
    logging_setup(args.loglevel)

    # Consume RSS
    threshold = datetime.now() - timedelta(days=args.days)
    candidates = process_rss(args.url)
    if len(candidates) < 1:
        logger.info(f'No new RSS entries within the last {args.days} day(s), exiting!')
        return

    access_token = read_secret(args.access_token, args.secret_type)
    access_token_secret = read_secret(args.access_token_secret, args.secret_type)
    bearer_token = read_secret(args.bearer_token, args.secret_type)
    consumer_key = read_secret(args.consumer_key, args.secret_type)
    consumer_secret = read_secret(args.consumer_secret, args.secret_type)

    api2 = tweepy.Client(
        access_token=access_token,
        access_token_secret=access_token_secret,
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )

    if args.test_tweet is not None:
        logger.info(f'Tweeting: {args.test_tweet}')
        xtwitter_post_raw(api2, args.test_tweet)
        return

    time.sleep(2)
    user = api2.get_me()
    logger.info(f'X/Twitter username: {user.data.username}')
    logger.info(f'X/Twitter name: {user.data.name}')
    logger.info(f'X/Twitter id: {user.data.id}')

    urls = xtwitter_list_posted_urls(api2, user.data.id)
    tweeted = xtwitter_decode_urls(urls)

    posts = 0
    for candidate in candidates:
        if posts >= args.posts:
            logger.info(f"Stopping posting after reaching post limit: {posts}")
            break
        announce = True
        for old in tweeted:
            if candidate.link == old:
                logger.info(f"Disregard already published: {old}")
                announce = False
                break
        if announce:
            logger.debug(f"Prepare post: {candidate.link}")
            xtwitter_post(api2, candidate, args.dryrun)
            posts = posts + 1

    logger.info("Terminating normally. Thanks for All the Fish!")

if __name__ == "__main__":
    main()
