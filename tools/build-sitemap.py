"""Regenerate sitemap.xml from what actually exists on disk.

    python tools/build-sitemap.py

Run it after build-blog.py, and after adding or removing any page.

The old sitemap listed exactly one URL and was hand-maintained, which is
fine for a one-page site and stops being fine the moment there is a blog.
This reads the real files instead, so the sitemap cannot drift from what is
published - a stale sitemap is worse than none, because it teaches Google
URLs that are not there.

Blog URLs only appear once posts.json actually has posts. An empty archive
in the sitemap is an invitation to crawl a page with nothing on it.
"""
import json
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://talonconstructioncompany.com"

posts = json.loads((ROOT / "content" / "posts.json").read_text(encoding="utf-8"))["posts"]
posts = sorted(posts, key=lambda p: p["date"], reverse=True)

today = datetime.date.today().isoformat()

urls = [("%s/" % SITE, today, "monthly", "1.0")]

if posts:
    # The archive changes whenever the newest post does.
    urls.append(("%s/blog/" % SITE, posts[0]["date"], "weekly", "0.8"))
    for p in posts:
        urls.append(("%s/blog/%s/" % (SITE, p["slug"]), p["date"], "yearly", "0.6"))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, lastmod, freq, prio in urls:
    lines += ["  <url>",
              "    <loc>%s</loc>" % loc,
              "    <lastmod>%s</lastmod>" % lastmod,
              "    <changefreq>%s</changefreq>" % freq,
              "    <priority>%s</priority>" % prio,
              "  </url>"]
lines.append("</urlset>")

(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

print("sitemap.xml: %d URL(s)" % len(urls))
if not posts:
    print("  blog deliberately omitted - posts.json is empty")
