import atproto_client
import atproto_identity
from atproto import models
import html
import utils

class BotImplementationBSky:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.posted = []

    def startup(self):
        utils.logger.info(f'Bluesky bot implementation: startup')

        handle = utils.read_config(
                self.config,
                'bsky.handle')
        if handle is None:
            utils.logger.error("Error retrieving: bsky.handle")
            return False

        password = utils.read_config_secret(
                self.config,
                'bsky.secrets.password')
        if password is None:
            utils.logger.error("Error retrieving: bsky.secrets.password")
            return False

        did = bsky_lookup(handle)
        utils.logger.info(f"Bluesky lookup: {handle}={did}")

        client = atproto_client.client.client.Client()
        client.login(handle, password)

        posts = bsky_posts(client, did)
        posted = []
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
            posted.append(uri)
            utils.logger.debug(f"Bluesky embeded: {uri}")

        self.client = client
        self.posted = posted
        return True

    def post(self, rss_entry, dryrun):
        return bsky_post(
                self.client,
                rss_entry,
                dryrun)


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
    c_uri = candidate.link
    utils.logger.debug(f"c_title: {c_title}")
    utils.logger.debug(f"c_description: {c_description}")
    utils.logger.debug(f"c_uri: {c_uri}")

    embed_external = models.AppBskyEmbedExternal.Main(
        external = models.AppBskyEmbedExternal.External(
            title = c_title,
            description = c_description,
            uri = c_uri,
            )
    )
    text = "📣 " + c_title + " 📣 " + c_description
    text300 = utils.truncate( text, 300 )
    if dryrun:
        utils.logger.info(f"Dry-run post: {c_uri}")
    else:
        utils.logger.info(f"Post: {c_uri}")
        post = client.send_post( text=text300, embed=embed_external )
        utils.logger.info(f"post.uri: {post.uri}")
        utils.logger.info(f"post.cid: {post.cid}")
