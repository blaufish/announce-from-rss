#!.venv/bin/python3

import argparse
from datetime import datetime, timedelta
import feedparser
import re
import time
import yaml

import utils
from implementation_mastodon import BotImplementationMastodon
from implementation_bsky import BotImplementationBSky
from implementation_twitter import BotImplementationTwitter

threshold = None

class Limits:
    def __init__(self, max_days, max_posts, dryrun):
        self.max_days = max_days or 1
        self.max_posts = max_posts or 1
        self.dryrun = dryrun
        if dryrun is None:
            self.dryrun = True


def process_rss(url):
    candidates = []
    utils.logger.info(f"Request feed from: {url}")
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


def enabled(config, module):
    configured = utils.read_config(
            config,
            module)
    if configured is None:
        utils.logger.info(f'Bot implementation {module} not configured.')
        return False
    enabled = utils.read_config(
            config,
            module + '.enabled')
    if enabled is not None:
        if enabled is False:
            utils.logger.info(f'Bot implementation {module} is disabled.')
            return False
    return True


def transform_sakerhetspodcasten(candidates):
    for candidate in candidates:
        c_desc = candidate.description
        c_desc = re.sub(r"Lyssna mp3, längd: ", "", c_desc)
        c_desc = re.sub(r" Innehåll ", " ", c_desc)
        candidate.description = c_desc


def post_loop(implementation, candidates, limits):
    started = implementation.startup()
    if not started:
        return

    posts = 0
    for candidate in candidates:
        if posts >= limits.max_posts:
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
            implementation.post(candidate,
                                limits.dryrun)
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
            help = 'Configuration file location')

    args = parser.parse_args()

    config = None
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    loglevel = utils.read_config(config, 'loglevel')
    utils.logging_setup(loglevel or 'INFO')
    utils.logger.debug(f'Configuration loaded: {config}')

    url = utils.read_config(config, 'url')
    if url is None:
        utils.logger.error('No "url" to RSS channel in config file!')
        return

    limits = Limits(
            utils.read_config(config, 'limits.days'),
            utils.read_config(config, 'limits.posts'),
            utils.read_config(config, 'limits.dryrun'))

    if limits.dryrun:
        utils.logger.info('Dryrun: announcements are inhibited.')
    utils.logger.info(f'Limit: max announcements: {limits.max_posts}.')
    utils.logger.info(f'Limit: max days: {limits.max_days}.')

    threshold = datetime.now() - timedelta(days=limits.max_days)

    candidates = process_rss(url)
    if len(candidates) < 1:
        utils.logger.info(f'No new RSS entries within the last {limits.max_days} day(s), exiting!')
        return

    transformer = utils.read_config(config, 'transformer')
    if transformer is not None:
        match transformer:
            case 'sakerhetspodcasten':
                transform_sakerhetspodcasten(candidates)
            case _:
                utils.logger.error(f"Unknown transformer: {transformer}.")
                return


    implementations = [ ]
    if enabled(config, 'mastodon'):
        impl_m = BotImplementationMastodon(config)
        implementations.append(impl_m)

    if enabled(config, 'bsky'):
        impl_bsky = BotImplementationBSky(config)
        implementations.append(impl_bsky)

    if enabled(config, 'twitter'):
        impl_x = BotImplementationTwitter(config)
        implementations.append(impl_x)

    if len(implementations) < 1:
        utils.logger.error('No bot implementations configured?')
        return

    for implementation in implementations:
        post_loop(implementation, candidates, limits)

    utils.logger.info("Terminating normally. Thanks for All the Fish!")


if __name__ == "__main__":
    main()
