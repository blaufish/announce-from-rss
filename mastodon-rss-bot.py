#!.venv/bin/python3

import argparse
from datetime import datetime, timedelta
import feedparser
import html
import logging
import mastodon
from mastodon import Mastodon
import os
import re
import requests
import time

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

def mastodon_list_posted_urls(m, account):
    posts = None
    try:
        posts = m.account_statuses(account)
    except Exception as e:
        logger.error(f"m.statuses(...): {e}")
        return None
    urls = []
    for post in posts:
        strpost = post.content
        words = strpost.split()
        for word in words:
            url = None
            if word.startswith('href="http'):
                sp = word.split('"')
                url = sp[1]
            else:
                continue
            if url.startswith('https://'):
                pass
            elif url.startswith('http://'):
                pass
            else:
                continue
            if url in urls:
                continue
            urls.append(url)
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

def mastodon_post_raw(m, toot):
    out = m.status_post(status=toot)
    logger.info(f"Toot uri: {out['uri']}")
    logger.info(f"Toot text: {out['content']}")
    #print(out)
    #print(out.keys())

def mastodon_post(m, candidate, dryrun):
    c_title = candidate.title
    c_description = candidate.description

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

    padding = f'<p></p><p><a href="{c_uri}">{c_uri}</a></p>'
    padding_length = len(padding)

    truncated_len = 500 - padding_length
    text_truncate = truncate( text, truncated_len )
    text_final = f'<p>{text_truncate}</p><p><a href="{c_uri}">{c_uri}</a></p>'

    if dryrun:
        logger.info(f"Dry-run post: {c_uri}")
    else:
        logger.info(f"Post: {c_uri}")
        mastodon_post_raw(m, text_final)

def truncate( text, maxlen ):
    if len(text) < maxlen:
        return text
    idx = text.rfind(" ", 0, maxlen-3)
    return text[:idx] + "..."

def main():
    global threshold

    # Mastodon defaults
    LOCAL_TEST_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    API_BASE_URI = 'https://mastodon.social'

    parser = argparse.ArgumentParser(
            prog = 'mastodon-rss-bot.py',
            description = 'mastodon bot',
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
            help = '"Your access token" in application settings')
    parser.add_argument('--client-key',
            dest = 'client_key',
            required = True,
            help = '"Client key" in application settings')
    parser.add_argument('--client-secret',
            dest = 'client_secret',
            required = True,
            help = '"Client secret" in application settings')
    parser.add_argument('--secret-type',
            dest = 'secret_type',
            required = True,
            choices = ['arg', 'env', 'file'],
            help = 'secret type/source')
    #
    # Optional arguments
    #
    parser.add_argument('--api-base-url',
            dest = 'api_base_url',
            default = API_BASE_URI,
            help = f'Default {API_BASE_URI}')
    parser.add_argument('--redirect-uri',
            dest = 'redirect_uri',
            default = LOCAL_TEST_REDIRECT_URI,
            help = f'"Redirect URI" in application settings, default {LOCAL_TEST_REDIRECT_URI}')
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
    parser.add_argument('--test-toot',
            dest = 'test_toot',
            default = None,
            help = 'A test toot, e.g. "hello world testing API"')

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
    client_key = read_secret(args.client_key, args.secret_type)
    client_secret = read_secret(args.client_secret, args.secret_type)

    m = Mastodon(
            access_token=args.access_token,
            api_base_url=args.api_base_url)

    if args.test_toot is not None:
        logger.info(f'Tooting: {args.test_toot}')
        mastodon_post_raw(m, args.test_toot)
        return

    user = m.me()
    logger.info(f'Mastodon id: {user.id}')
    logger.info(f'Mastodon username: {user.username}')
    logger.info(f'Mastodon acct: {user.acct}')
    logger.info(f'Mastodon display name: {user.display_name}')

    #urls = xtwitter_list_posted_urls(api2, user.data.id)
    #tweeted = xtwitter_decode_urls(urls)
    #tweeted = []
    tweeted = mastodon_list_posted_urls(m, user)

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
            mastodon_post(m, candidate, args.dryrun)
            posts = posts + 1

    logger.info("Terminating normally. Thanks for All the Fish!")

if __name__ == "__main__":
    main()
