from mastodon import Mastodon
import utils

# Mastodon defaults
API_BASE_URI = 'https://mastodon.social'

class BotImplementationMastodon:
    def __init__(self, config):
        self.config = config
        self.m = None
        self.posted = []

    def startup(self):
        utils.logger.info(f'Mastodon bot implementation: startup')

        access_token = utils.read_config_secret(
                self.config,
                'mastodon.secrets.access_token')
        if access_token is None:
            utils.logger.error("Error retrieving: mastodon.secrets.access_token")
            return False

        api_base_url = utils.read_config(
                self.config,
                'mastodon.api_base_uri') or API_BASE_URI

        m = Mastodon(
                access_token = access_token,
                api_base_url = api_base_url)

        user = m.me()
        utils.logger.info(f'Mastodon id: {user.id}')
        utils.logger.info(f'Mastodon username: {user.username}')
        utils.logger.info(f'Mastodon acct: {user.acct}')
        utils.logger.info(f'Mastodon display name: {user.display_name}')

        posted = mastodon_list_posted_urls(
                m,
                user)

        self.m = m
        self.posted = posted
        return True

    def post(rss_entry, dryrun):
        return mastodon_post(
                self.m,
                rss_entry,
                dryrun)


def mastodon_list_posted_urls(m, account):
    posts = None
    try:
        posts = m.account_statuses(account)
    except Exception as e:
        utils.logger.error(f"m.statuses(...): {e}")
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


def mastodon_post_raw(logger, m, toot):
    out = m.status_post(status=toot)
    utils.logger.info(f"Toot uri: {out['uri']}")
    utils.logger.info(f"Toot text: {out['content']}")


def mastodon_post(m, candidate, dryrun):
    c_title = candidate.title
    c_description = candidate.description
    c_uri = candidate.link

    utils.logger.debug(f"c_title: {c_title}")
    utils.logger.debug(f"c_description: {c_description}")
    utils.logger.debug(f"c_uri: {c_uri}")

    text = "📣 " + c_title + " 📣 " + c_description

    c_uri_len = len(c_uri)
    if c_uri_len > 200:
        logger.error(f'Insanely long URI causing error: {c_uri}')
        return

    padding = f'<p></p><p><a href="{c_uri}">{c_uri}</a></p>'
    padding_length = len(padding) + 5 # just some additional safety

    truncated_len = 500 - padding_length
    text_truncate = truncate( text, truncated_len )
    text_final = f'{text_truncate}\n{c_uri}'

    if dryrun:
        utils.logger.info(f"Dry-run post: {c_uri}")
    else:
        utils.logger.info(f"Post: {c_uri}")
        mastodon_post_raw(m, text_final)
