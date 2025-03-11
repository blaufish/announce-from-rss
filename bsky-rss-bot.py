#!.venv/bin/python3

import argparse
import atproto_client
import atproto_identity
from atproto import models
from datetime import datetime, timedelta
import feedparser
import logging
import os
import re
import time
import yaml

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

def main():
    global threshold
    parser = argparse.ArgumentParser(
            prog = 'bsky-rss-bot.py',
            description = 'bluesky bot',
            epilog = 'Hope this help was helpful! :-)')
    #
    # Required arguments
    #
    parser.add_argument('--url',
            dest = 'url',
            required = True,
            help = 'URL to lib-syn RSS feed, e.g. https://sakerhetspodcasten.se/index.xml')
    parser.add_argument('--handle',
            dest = 'handle',
            required = True,
            help = 'bluesky handle')
    parser.add_argument('--secret',
            dest = 'secret',
            required = True,
            help = 'bluesky secret')
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

    secret = None
    match args.secret_type:
        case "arg":
            content = args.secret
            secret = content.strip()
        case "env":
            content = os.environ[args.secret]
            secret = content.strip()
        case "file":
            with open(args.secret, "r") as f:
                content = f.read();
                secret = content.strip()
        case "_":
            logger.error(f"TODO implement!")
            return

    threshold = datetime.now() - timedelta(days=args.days)

    candidates = process_rss(args.url)

    if len(candidates) < 1:
        logger.info("No candiates, exiting")
        return

    did = bsky_lookup(args.handle)
    logger.info(f"Bluesky lookup: {args.handle}={did}")
    client = atproto_client.client.client.Client()
    client.login(args.handle, secret)
    posts = bsky_posts(client, did)

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
