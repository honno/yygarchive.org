# yygarchive.org

A searchable archive of the old YoYo Games Sandbox, preserving 100k+ GameMaker projects from 2007 to 2014.

For more information see [yygarchive.org/about](https://yygarchive.org/about) :)

## Technical notes

Games are hosted on the Internet Archive; this site provides search and browsing over the metadata.

It uses vanilla HTML/CSS/JS for the frontend, and generates static pages with [Jinja2](https://github.com/pallets/jinja). I use [GitHub Pages](https://docs.github.com/en/pages) for hosting.

### Metadata store

All game metadata lives in a single `games.json` file (~50 MB, ~100k entries). The entire file is fetched on loading the homepage and held in memory, enabling fully client-side search and filtering.

The initial load can be slow on poor connections, but once downloaded, search, filter, and sort operations are instant.

### Static site generation

Previously the site had a Flask backend (see the [old-flask](https://github.com/honno/yygarchive.org/tree/old-flask) branch). Now pages are built from Jinja2 templates in `templates/` using `build.py`, which outputs to `_site/`.
GitHub Actions runs `python build.py --all` and deploys `_site/` to GitHub Pages.

A Flask-based server (`serve.py`) can render these templates on the fly for local development.


### Legacy URL redirects

The old Flask site had `/developer/<name>` paths for every developer. Having these dedicated pages for authors didn't seem worth the maintenance burden, but I still want to preserve the existing links.

GitHub Pages has no SPA routing support, so having `index.html` preserve these paths isn't possible. As a hack requests to these paths are caught by `404.html`, which redirects to `/#developer=<name>`.

Note this redirect behaviour isn't replicated in `serve.py`, so for local development you will just get a normal 404.