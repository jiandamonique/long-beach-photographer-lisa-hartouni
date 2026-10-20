#!/usr/bin/env python3
"""
generate_rss.py — Auto-generate rss.xml from blog HTML files.

This script scans all blog-*.html files in the repo root, extracts
metadata from their <head> tags, and writes a fresh rss.xml.

Usage (local or in GitHub Actions):
    python scripts/generate_rss.py

Run from the repo root. Writes rss.xml to the repo root.
"""

import os
import re
import sys
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime

# ── Configuration ──────────────────────────────────────────────────────────────

SITE_BASE = "https://jiandamonique.github.io/long-beach-photographer-lisa-hartouni"
CHANNEL_TITLE = "Lisa Hartouni — Blog"
CHANNEL_DESCRIPTION = (
    "News, updates, and press about Lisa Hartouni's photography and community projects."
)
CHANNEL_LINK = f"{SITE_BASE}/blog.html"
RSS_SELF_LINK = f"{SITE_BASE}/rss.xml"

# Non-blog pages to skip even if named blog-*.html
SKIP_FILES = {"blog.html"}  # the blog index, not a post

# Work from the directory this script is called from (repo root when run via Action)
REPO_ROOT = os.getcwd()

# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_meta(html: str, property_name: str) -> str:
    """Extract content from <meta name="..." content="..."> or <meta property="..." content="...">."""
    # Try property="..." first (og:, article:, etc.)
    m = re.search(
        rf'<meta\s+property=["\']?{re.escape(property_name)}["\']?\s+content=["\']([^"\']*)["\']',
        html, re.IGNORECASE
    )
    if not m:
        # Try name="..."
        m = re.search(
            rf'<meta\s+name=["\']?{re.escape(property_name)}["\']?\s+content=["\']([^"\']*)["\']',
            html, re.IGNORECASE
        )
    if not m:
        # Try reversed attribute order
        m = re.search(
            rf'<meta\s+content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']?{re.escape(property_name)}["\']?',
            html, re.IGNORECASE
        )
    return m.group(1).strip() if m else ""


def extract_title(html: str) -> str:
    """Extract from <title> tag, strip ' — Lisa Hartouni' suffix if present."""
    m = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
    if not m:
        return ""
    title = m.group(1).strip()
    # Strip the site name suffix
    for suffix in [" — Lisa Hartouni", " - Lisa Hartouni"]:
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
    return title


def iso_to_rfc822(iso_date: str) -> str:
    """Convert '2026-10-14' or '2026-10-14T...' to RFC 822."""
    # Strip time portion if present
    date_part = iso_date[:10]
    try:
        dt = datetime.strptime(date_part, "%Y-%m-%d")
        # Attach PDT offset (UTC-7); close enough for a Pacific-based site
        pdt = timezone(timedelta(hours=-7))
        dt = dt.replace(tzinfo=pdt)
        return format_datetime(dt)
    except ValueError:
        return ""


def xml_escape(text: str) -> str:
    """Escape characters that break XML."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )


def scan_blog_posts(repo_root: str) -> list[dict]:
    """Return a list of post dicts sorted newest-first."""
    posts = []
    for fname in os.listdir(repo_root):
        if not fname.startswith("blog-") or not fname.endswith(".html"):
            continue
        if fname in SKIP_FILES:
            continue

        path = os.path.join(repo_root, fname)
        try:
            with open(path, encoding="utf-8") as f:
                html = f.read()
        except Exception as e:
            print(f"  WARN: could not read {fname}: {e}", file=sys.stderr)
            continue

        title = extract_title(html)
        description = extract_meta(html, "description")
        pub_date_iso = extract_meta(html, "article:published_time")
        canonical = extract_meta(html, "og:url")
        if not canonical:
            canonical = f"{SITE_BASE}/{fname}"

        if not title:
            print(f"  WARN: no <title> found in {fname}, skipping", file=sys.stderr)
            continue
        if not pub_date_iso:
            print(f"  WARN: no article:published_time in {fname}, skipping", file=sys.stderr)
            continue

        pub_date_rfc = iso_to_rfc822(pub_date_iso)
        if not pub_date_rfc:
            print(f"  WARN: could not parse date '{pub_date_iso}' in {fname}, skipping", file=sys.stderr)
            continue

        posts.append({
            "filename": fname,
            "title": title,
            "description": description,
            "link": canonical,
            "guid": canonical,
            "pub_date_iso": pub_date_iso,
            "pub_date_rfc": pub_date_rfc,
        })

    # Sort newest first
    posts.sort(key=lambda p: p["pub_date_iso"], reverse=True)
    return posts


def build_rss(posts: list[dict]) -> str:
    """Build the full RSS XML string."""
    now_rfc = format_datetime(datetime.now(timezone(timedelta(hours=-7))))
    latest_rfc = posts[0]["pub_date_rfc"] if posts else now_rfc

    items_xml = []
    for p in posts:
        item = f"""  <item>
    <title>{xml_escape(p['title'])}</title>
    <link>{xml_escape(p['link'])}</link>
    <guid>{xml_escape(p['guid'])}</guid>
    <pubDate>{p['pub_date_rfc']}</pubDate>
    <description>{xml_escape(p['description'])}</description>
  </item>"""
        items_xml.append(item)

    items_block = "\n\n".join(items_xml)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{xml_escape(CHANNEL_TITLE)}</title>
  <link>{CHANNEL_LINK}</link>
  <atom:link href="{RSS_SELF_LINK}" rel="self" type="application/rss+xml" />
  <description>{xml_escape(CHANNEL_DESCRIPTION)}</description>
  <language>en-us</language>
  <lastBuildDate>{latest_rfc}</lastBuildDate>

  <!--
    AUTO-GENERATED by scripts/generate_rss.py — do not edit by hand.
    To change a post's RSS entry, update the blog HTML file's <head> metadata:
      - <title> sets the item title
      - <meta name="description"> sets the item description
      - <meta property="article:published_time"> sets the pubDate
      - <meta property="og:url"> sets the link/guid
    Then re-run this script (or wait for the daily GitHub Action to run).
  -->

{items_block}

</channel>
</rss>
"""


def main():
    print(f"Scanning for blog posts in: {REPO_ROOT}")
    posts = scan_blog_posts(REPO_ROOT)
    print(f"Found {len(posts)} posts.")
    for p in posts:
        print(f"  {p['pub_date_iso']}  {p['filename']}")

    if not posts:
        print("No posts found — rss.xml not written.", file=sys.stderr)
        sys.exit(1)

    rss_xml = build_rss(posts)
    out_path = os.path.join(REPO_ROOT, "rss.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"\nWrote {out_path}  ({len(rss_xml)} bytes)")


if __name__ == "__main__":
    main()
