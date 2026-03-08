# yygarchive.org

A searchable archive of the old YoYo Games Sandbox, preserving 100k+ GameMaker projects from 2007 to 2014.

For more information see [yygarchive.org#about](https://yygarchive.org/#about) :)

## Technical notes

Games are actually hosted on the Internet Archive; this site simply provides search and browsing over the metadata. It uses vanilla HTML/CSS/JS, hosted on GitHub Pages.

### Metadata store

All game metadata lives in a single `games.json` file (~50 MB, ~100k entries). The entire file is fetched on page load and held in memory, enabling fully client-side search and filtering.

The initial load can be slow on poor connections, but once downloaded, search, filter, and sort operations are instant. Previously yygarchive had a backend (see the [old-flask](https://github.com/honno/yygarchive.org/tree/old-flask) branch), which I moved away from since a static site means I can just dump everything on GitHub Pages without thinking about hosting.

### Redirecting legacy URL paths

The previous iteration of yygarchive had separate pages for games and developers with paths like `yygarchive.org/game/118428`. Unfortunately GitHub doesn't support single-paged apps which could keep these links, so I had to make these links redirect instead.

To keep these links working, `404.html` intercepts these requests, converts the path to a hash fragment (e.g. `#game=118428` or `#dev=Ultimortal`), and redirects back to `/`. The main `index.html` then reads the hash and opens the appropriate modal or filter.

Ideal future work would be to actually make a static site generator for seperate game and author pages. This probably would really help SEO too :sweat_smile:
