import requests
import time
import tweepy
import utils

class BotImplementationTwitter:
    def __init__(self, config):
        self.config = config
        self.api2 = None
        self.posted = []

    def startup(self):
        utils.logger.info(f'X/Twitter bot implementation: startup')

        access_token = read_config_secret(
                self.config,
                'twitter.secrets.access_token')
        access_token_secret = read_config_secret(
                self.config,
                'twitter.secrets.access_token_secret')
        bearer_token = read_config_secret(
                self.config,
                'twitter.secrets.bearer_token')
        consumer_key = read_config_secret(
                self.config,
                'twitter.secrets.consumer_key')
        consumer_secret = read_config_secret(
                self.config,
                'twitter.secrets.consumer_secret')

        if access_token is None:
            utils.logger.error('Error retrieving: twitter.secrets.access_token')
            return False
        if access_token_secret is None:
            utils.logger.error('Error retrieving: twitter.secrets.access_token_secret')
            return False
        if bearer_token is None:
            utils.logger.error('Error retrieving: twitter.secrets.bearer_token')
            return False
        if consumer_key is None:
            utils.logger.error('Error retrieving: twitter.secrets.consumer_key')
            return False
        if consumer_secret is None:
            utils.logger.error('Error retrieving: twitter.secrets.consumer_secret')
            return False

        api2 = tweepy.Client(
            access_token=access_token,
            access_token_secret=access_token_secret,
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )

        time.sleep(2)
        user = api2.get_me()

        utils.logger.info(f'X/Twitter username: {user.data.username}')
        utils.logger.info(f'X/Twitter name: {user.data.name}')
        utils.logger.info(f'X/Twitter id: {user.data.id}')

        urls = xtwitter_list_posted_urls(api2, user.data.id)
        posted = xtwitter_decode_urls(urls)

        self.api2 = api2
        self.posted = posted
        return True

    def post(self, rss_entry, dryrun):
        return xtwitter_post(
                self.api2,
                rss_entry,
                dryrun)


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
    c_uri = candidate.link

    logger.debug(f"c_title: {c_title}")
    logger.debug(f"c_description: {c_description}")
    logger.debug(f"c_uri: {c_uri}")

    text = "📣 " + c_title + " 📣 " + c_description

    c_uri_len = len(c_uri)
    if c_uri_len > 200:
        logger.error(f'Insanely long URI causing error: {c_uri}')
        return

    truncated_len = 240 - 1 - c_uri_len
    text_truncate = utils.truncate( text, truncated_len )
    text_final = text_truncate + '\n' + c_uri

    if dryrun:
        logger.info(f"Dry-run post: {c_uri}")
    else:
        logger.info(f"Post: {c_uri}")
        xtwitter_post_raw(api2, text_final)
