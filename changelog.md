# v0.0.1

Files:
``` plain
R100	bluesky-announce-from-rss/.gitattributes	.gitattributes
A	.gitignore
A	Dockerfile
A	README.md
D	bluesky-announce-from-rss/.gitignore
D	bluesky-announce-from-rss/README.md
D	bluesky-announce-from-rss/bsky-rss-bot.py
D	bluesky-announce-from-rss/requirements.in
D	bluesky-announce-from-rss/requirements.txt
D	bluesky-announce-from-rss/venv.sh
A	build.sh
A	example.yaml
A	implementation_bsky.py
A	implementation_mastodon.py
A	implementation_twitter.py
D	mastodon-announce-from-rss/.gitattributes
D	mastodon-announce-from-rss/.gitignore
D	mastodon-announce-from-rss/README.md
D	mastodon-announce-from-rss/mastodon-rss-bot.py
D	mastodon-announce-from-rss/requirements.txt
D	mastodon-announce-from-rss/spellcheck.sh
D	mastodon-announce-from-rss/venv.sh
A	release.sh
R051	mastodon-announce-from-rss/requirements.in	requirements.in
A	requirements.lock
A	requirements.txt
A	rss-bot.py
R100	bluesky-announce-from-rss/spellcheck.sh	spellcheck.sh
D	twitter-announce-from-rss/.gitattributes
D	twitter-announce-from-rss/.gitignore
D	twitter-announce-from-rss/README.md
D	twitter-announce-from-rss/requirements.in
D	twitter-announce-from-rss/requirements.txt
D	twitter-announce-from-rss/spellcheck.sh
D	twitter-announce-from-rss/twitter-rss-bot.py
D	twitter-announce-from-rss/venv.sh
A	utils.py
A	venv.sh
```

Commits:
``` plain
* e282ee0 release.sh: v0.0.1
* 9539a75 Build scripts
* c9ef6de Documentation updates
* 4f322d3 Documentation
* 312aaaf Ignore spellchecker backup files
* 93f5730 Fix misspelling
* ed41c2a Ignore local test files
* fd70705 Move from arguments to configuration
* f35ec7f Fix twitter implementation
* 815eeb5 Gracefully handle secret not in readable file
* 25b1e4b Gracefully handle secret not in environment
* 02ab882 requirements.lock support
* 282c61c Twitter integration
* 3248eeb Remove execute permissions
* 677aa04 implementation_bsky
* e590b81 Improvements :)
* 5de4889 ignore __pycache__
* 9a5c177 Remove outdated README.md
* ee3f7a4 Begin rewrite as a single code base
* c358378 .gitignore
* 425fdce .gitattributes
```

# v0.0.0

Commits:
``` plain
*-.   1797822 Merge different repos into monorepo
|\ \  
| | * 7814cdf Prepare branch for merge
| | * e51817a git repo setup: .gitattributes .gitignore
| | * 6f82915 Lets remove the test snippet
| | * 4caf445 Lets memorialize this little test snippet
| | * 2b405e6 Documentation + spellchecker
| | * 8b931c0 Virtual environment
| | * d765612 Implement tweeting :)
| | * 3e20c8c Check RSS first, exit early if possible
| | * ac00dd0 Add a test-tweet feature
| | * 0003816 Cleanup
| | * 2600199 Initial draft code
| * 08806f5 Prepare branch for merge
| * ca2fba8 Convert entities, e.g. &amp; to &
| * 323c282 Delete dead code: timestruct_to_isoformat
| * 60781fa RSS to Bluesky announcer
* 3ee097a Prepare branch for merge
* 1ae2d61 Fix auth completely broken
* f9a051f Remove dead code, tweak formatting
* c185fa9 Remove dead code
* 22ce4bb README.md
* 4689448 Well. This seems to be working.
* a462751 Mastadonifying code a bit more
* c5e6cef Mastodonify a bit more
* fe5043a Begin mastodonify code
* 763a3bd Begin mastodonifying code base
* 723cd82 Squash twitter-announce-from-rss/master
```
