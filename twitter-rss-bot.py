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

def xtwitter_posted_urls(api2, user_id):
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
    urls2 = []
    for url in urls:
        decoded_url = xtwitter_decode_url(url)
        if decoded_url in urls2:
            continue
        urls2.append(decoded_url)
        logger.debug(f'X/Twitter URL {url}: {decoded_url}')
    return urls2

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
            help = 'bluesky secret type')
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

    # prase
    args = parser.parse_args()

    #
    # Set and validate globals
    #
    logging_setup(args.loglevel)
    #
    # Actually run the program
    #

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

    user = api2.get_me()
    logger.info(f'X/Twitter username: {user.data.username}')
    logger.info(f'X/Twitter name: {user.data.name}')
    logger.info(f'X/Twitter idi: {user.data.id}')

    urls = xtwitter_posted_urls(api2, user.data.id)
    if urls is None:
        return

    threshold = datetime.now() - timedelta(days=args.days)

    candidates = process_rss(args.url)

    if len(candidates) < 1:
        logger.info("No candiates, exiting")
        return


    tweeted = []
    for entry in posts.feed:
        post = entry.post
        record = post.record
        embed = post.embed
        if embed is None:
            continue
        if embed.py_type != 'app.bsky.embed.external#view':
            continue
        external = embed.external
        uri = external.uri
        tweeted.append(uri)
        logger.debug(f"Bluesky embeded: {uri}")

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
            bsky_post(client, candidate, args.dryrun)
            posts = posts + 1

    logger.info("Terminating normally. Thanks for All the Fish!")

def bsky_lookup(_id):
    resolver = atproto_identity.handle.resolver.HandleResolver()
    did = resolver.resolve(_id)
    return did

def bsky_posts(client, did):
    responses = client.get_author_feed(
        actor=did,
        filter='posts_and_author_threads',
        limit=30
        )
    return responses

def bsky_post(client, candidate, dryrun):
    c_title = candidate.title
    c_description = candidate.description
    # Convert entities, e.g. &amp; to &
    c_description = html.unescape( c_description )
    c_desc = re.sub(r"Lyssna mp3, längd: ", "", c_description)
    c_desc = re.sub(r" Innehåll ", " ", c_desc)
    c_uri = candidate.link
    logger.debug(f"c_title: {c_title}")
    logger.debug(f"c_description: {c_description}")
    logger.debug(f"c_desc: {c_desc}")
    logger.debug(f"c_uri: {c_uri}")

    embed_external = models.AppBskyEmbedExternal.Main(
        external = models.AppBskyEmbedExternal.External(
            title = c_title,
            description = c_desc,
            uri = c_uri,
            )
    )
    text = "📣 " + c_title + " 📣 " + c_desc
    text300 = truncate( text, 300 )
    if dryrun:
        logger.info(f"Dry-run post: {c_uri}")
    else:
        logger.info(f"Post: {c_uri}")
        post = client.send_post( text=text300, embed=embed_external )
        logger.info(f"post.uri: {post.uri}")
        logger.info(f"post.cid: {post.cid}")

def truncate( text, maxlen ):
    if len(text) < maxlen:
        return text
    idx = text.rfind(" ", 0, maxlen-3)
    return text[:idx] + "..."

if __name__ == "__main__":
    main()
