# Lisa Hartouni — Site (Stand-In Page)

This is a **stand-in page**, not the final site. It exists so Lisa has a clean, live "home base" to point people to (press, LinkedIn, GoFundMe, etc.) while her real website is rebuilt on her own hosting.

Once her permanent site is set up on her own host (Namecheap, at one of her existing domains — lhartouni.com, lisahartouni.com, intersectionsproject.com, myphotorecords.com, or fromheretomanzanar.com), this page should be retired or redirected there. Nothing here is meant to be the long-term home for her work.

## What's in this repo

- `index.html` — the entire site (a single self-contained page: structure, styles, and content all in one file).

## Design notes

- **Palette**: based on the "Muted Grays and Blues" scheme (light blue-grays for backgrounds, panels, and borders), with one warm rust accent color (`--accent`) reserved only for buttons and links that need to get clicked — donate/support CTAs, mainly. Everything else stays quiet on purpose, to match Lisa's own low-key personality.
- **Type**: Newsreader (serif, for headings) + IBM Plex Sans (body). Loaded from Google Fonts via `<link>` tags in `index.html` — requires an internet connection to display correctly; falls back to system fonts otherwise.
- **No tabs, no JS-driven UI** — everything is a single scrolling page with anchor-link navigation, on purpose, to keep it simple and easy for Lisa to hand-edit later without needing to touch any JavaScript.
- **Content** is pulled directly from Lisa's bio, project descriptions, and the live GoFundMe campaign copy — nothing invented. Update the timeline, project cards, and press list directly in `index.html` as things change.

## To publish this on GitHub Pages

1. Push this repo to GitHub.
2. In the repo's Settings → Pages, set the source to the `main` branch, root folder.
3. GitHub will publish it at `https://<username>.github.io/<repo-name>/`.

## To retire this page later

Once Lisa's real site is live on her own domain, either:
- Replace the content of `index.html` with a redirect to the new site, or
- Delete/archive this repo entirely and update any links (LinkedIn, GoFundMe, social bios) to point to the new site instead.
