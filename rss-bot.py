#!.venv/bin/python3

import argparse
from datetime import datetime, timedelta
import feedparser
import os
import re
import time
import yaml

import utils
from implementation_mastodon import BotImplementationMastodon

threshold = None

def process_rss(url):
    candidates = []
    utils.logger.info(f"Request feed from {url}")
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
        utils.logger.info(f"RSS candidate: {title}")
        return True
    else:
        utils.logger.debug(f"RSS skipping old entry: {title}")
        return False

def post_loop(implementation, max_posts):
    implementation.startup()
    if not implementation.enabled:
        return

    posts = 0
    for candidate in candidates:
        if posts >= max_posts:
            utils.logger.info(f"Stopping posting after reaching post limit: {posts}")
            break
        announce = True
        for old in implementation.posted:
            if candidate.link == old:
                utils.logger.info(f"Disregard already published: {old}")
                announce = False
                break
        if announce:
            utils.logger.debug(f"Prepare post: {candidate.link}")
            implementation.post(candidate, args.dryrun)
            posts = posts + 1

def main():
    global threshold

    parser = argparse.ArgumentParser(
            prog = 'rss-bot.py',
            description = 'rss announcer bot',
            epilog = 'Hope this help was helpful! :-)')
    #
    # Required arguments
    #
    parser.add_argument('--config',
            dest = 'config',
            required = True,
            help = 'URL to lib-syn RSS feed, e.g. https://sakerhetspodcasten.se/index.xml')
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
            default = None,
            help = 'Maximum posts to emit, avoid spamming')

    args = parser.parse_args()

    utils.logging_setup(args.loglevel)

    config = None
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
        utils.logger.debug(f'Configuration loaded: {config}')

    url = utils.read_config(config, 'url')
    if url is None:
        utils.logger.error('No "url" to RSS channel in config file!')
        return

    threshold = datetime.now() - timedelta(days=args.days)

    candidates = process_rss(url)
    if len(candidates) < 1:
        utils.logger.info(f'No new RSS entries within the last {args.days} day(s), exiting!')
        return

    impl_m = BotImplementationMastodon(config)
    implementations = [
            impl_m,
            ]

    for implementation in implementations:
        post_loop(implementation, args.days)

    utils.logger.info("Terminating normally. Thanks for All the Fish!")


if __name__ == "__main__":
    main()
