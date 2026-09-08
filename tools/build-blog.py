"""Generate Talon's blog from content/posts.json.

    python tools/build-blog.py

Writes:
    blog/index.html         the archive, with the category filter
    blog/<slug>/index.html  one page per post

Never hand-edit anything under blog/ - this script overwrites it.

## Why a generator rather than hand-written pages

The full site rebuild is targeted at December 2026 and gated on the rebrand
decision. Posts written as data survive that; posts written as HTML get
rewritten. When the rebuild happens, this file changes and posts.json does
not.

## Design

Everything visual is taken from the LIVE site's own tokens in
css/styles.css - Bitter/Inter, oxblood, gold, bone. Note that BRAND-GUIDE.md
currently describes a different system (Tinos/Montserrat, #8B1A1A); the blog
follows the site it lives on, and the discrepancy is flagged for Kim rather
than silently resolved here.

## Two deliberate refusals

1. **The blog is not linked from the site until a post exists.** An empty
   "Blog" link in the header is worse than no link.
2. **The filter never hides a post from a crawler or a no-JS visitor.** Every
   post ships in the archive markup; the filter only sets a data attribute
   that CSS acts on. Turn JavaScript off and you get all of them.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "content" / "posts.json"
SITE = "https://talonconstructioncompany.com"

data = json.loads(DATA.read_text(encoding="utf-8"))
posts = data["posts"]
tags = data.get("tags", [])

# Newest first, and fail loudly on a duplicate slug rather than silently
# overwriting a live URL.
posts = sorted(posts, key=lambda p: p["date"], reverse=True)
slugs = [p["slug"] for p in posts]
dupes = {s for s in slugs if slugs.count(s) > 1}
if dupes:
    sys.exit("duplicate slug(s), each would overwrite the other: %s" % ", ".join(sorted(dupes)))

for p in posts:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", p["slug"]):
        sys.exit("bad slug %r - lowercase, digits and hyphens only" % p["slug"])
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p["date"]):
        sys.exit("bad date %r on %s - want YYYY-MM-DD" % (p["date"], p["slug"]))
    if p.get("tag") and p["tag"] not in tags:
        sys.exit("post %s has tag %r which is not in the tags list" % (p["slug"], p["tag"]))


def esc(s):
    return html.escape(s or "", quote=False)


def attr(s):
    return html.escape(s or "", quote=True)


def pretty_date(iso):
    y, m, d = iso.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return "%s %d, %s" % (months[int(m) - 1], int(d), y)


HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Google tag (gtag.js) - GA4 property "talonconstructioncompany.com" (545542659) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-PLTBXX30WR"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-PLTBXX30WR');
  </script>
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/png" href="/assets/talon-logo.png">
  <link rel="apple-touch-icon" href="/assets/talon-logo.png">
  <meta name="theme-color" content="#8B1E2D">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bitter:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/styles.css?v=4">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Talon Construction Company">
  <meta property="og:locale" content="en_US">
  <meta property="og:type" content="{og_type}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{og_image}">
  <meta property="og:image:alt" content="{og_image_alt}">
{extra_meta}{schema}
</head>
<body>

  <a href="#main" class="skip-link">Skip to content</a>

  <header class="site-header">
    <div class="wrap header-inner">
      <a href="/" class="brand">
        <img src="/assets/talon-logo.png" alt="" class="brand-logo" width="40" height="40">
        <span class="brand-name">Talon Construction Company</span>
      </a>
      <nav class="header-actions">
        <a href="tel:+15304323633" class="header-phone">(530)&nbsp;432&#8209;3633</a>
        <a href="/#contact" class="btn btn-gold">Start Your Project</a>
      </nav>
    </div>
  </header>

  <main id="main">
"""

# Copied from index.html so a blog page is visibly the same site. The only
# addition is the Journal link in the nav line - everything else, including
# the CSLB number and the tagline, is the live footer verbatim.
FOOT = """  </main>

  <footer class="site-footer">
    <div class="wrap footer-inner">
      <img src="/assets/talon-logo.png" alt="Talon Construction Company logo" class="footer-logo" width="72" height="76">
      <div class="footer-meta">
        <p class="footer-name">Talon Construction Company</p>
        <p>Penn Valley, California</p>
        <p>California Licensed General Contractor &middot; CSLB #397350</p>
        <p>Phone: <a href="tel:+15304323633">(530) 432&#8209;3633</a> &middot; Website: <a href="https://www.talonconstructioncompany.com">www.talonconstructioncompany.com</a></p>
        <p><a href="/">Home</a> &middot; <a href="/blog/">The Journal</a> &middot; <a href="/#contact">Start Your Project</a></p>
        <p class="footer-tagline">Careful planning. Honest communication. Work built to last.</p>
        <p class="footer-fine">&copy; 2026 Talon Construction Company. All rights reserved.</p>
      </div>
    </div>
  </footer>

</body>
</html>
"""


def placeholder(kind):
    """Branded stand-in so a post without art reads as deliberate, not broken.

    Kim supplies images later; this is what holds the slot meanwhile, at the
    same aspect ratio so nothing shifts when the real image lands.
    """
    return (
        '<div class="post-figure post-figure-placeholder post-figure-%s" aria-hidden="true">'
        '<img src="/assets/talon-logo.png" alt="" width="64" height="64">'
        "</div>" % kind
    )


def figure(post, kind):
    src = post.get("image_wide" if kind == "wide" else "image", "")
    if not src:
        return placeholder(kind)
    ratio = "2 / 1" if kind == "wide" else "3 / 2"
    return (
        '<div class="post-figure post-figure-%s">'
        '<img src="%s" alt="%s" loading="lazy" style="aspect-ratio:%s">'
        "</div>" % (kind, attr(src), attr(post.get("image_alt", "")), ratio)
    )


# Confirmed by Kim 2026-09-02. LinkedIn and YouTube are still unverified and
# deliberately absent - a wrong sameAs is worse than a missing one.
SOCIAL = [
    "https://www.facebook.com/talonconstructionco",
    "https://www.instagram.com/talonconstructionco",
]


def org_node():
    return {
        "@type": "Organization",
        "name": "Talon Construction Company",
        "url": SITE + "/",
        "telephone": "+1-530-432-3633",
        "logo": {"@type": "ImageObject", "url": "%s/assets/talon-logo.png" % SITE},
        "sameAs": list(SOCIAL),
    }


def crumbs(trail):
    """BreadcrumbList from [(name, url), ...]."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
            for i, (n, u) in enumerate(trail)
        ],
    }


def ld(*blocks):
    return "\n".join(
        '  <script type="application/ld+json">\n%s\n  </script>'
        % json.dumps(b, indent=2) for b in blocks)


def post_page(post, newer, older):
    body = "\n".join("      <p>%s</p>" % esc(t) for t in post["paragraphs"])

    meta = ['<span class="post-date">%s</span>' % pretty_date(post["date"])]
    if post.get("tag"):
        meta.append('<span class="post-tag">%s</span>' % esc(post["tag"]))
    if post.get("area"):
        meta.append('<span class="post-area">%s</span>' % esc(post["area"]))

    nav = []
    if older:
        nav.append('<a class="post-nav-prev" href="/blog/%s/">&larr; %s</a>'
                   % (older["slug"], esc(older["title"])))
    if newer:
        nav.append('<a class="post-nav-next" href="/blog/%s/">%s &rarr;</a>'
                   % (newer["slug"], esc(newer["title"])))

    url = "%s/blog/%s/" % (SITE, post["slug"])
    image = (SITE + post["image_wide"]) if post.get("image_wide") \
        else "%s/assets/hero-1920.jpg" % SITE
    modified = post.get("date_modified") or post["date"]

    article = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "datePublished": post["date"],
        "dateModified": modified,
        "description": post["excerpt"],
        "image": image,
        "inLanguage": "en-US",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "isPartOf": {"@type": "Blog", "@id": "%s/blog/#journal" % SITE,
                     "name": "The Journal"},
        "author": org_node(),
        "publisher": org_node(),
    }
    if post.get("tag"):
        article["articleSection"] = post["tag"]
    if post.get("area"):
        # The post is genuinely about this place - say so in the graph as well
        # as on the card. This is the local half of why the blog exists.
        article["contentLocation"] = {
            "@type": "Place",
            "name": "%s, California" % post["area"],
        }

    schema = ld(article, crumbs([
        ("Home", SITE + "/"),
        ("The Journal", "%s/blog/" % SITE),
        (post["title"], url),
    ]))

    head = HEAD.format(
        title="%s | Talon Construction Company" % esc(post["title"]),
        description=attr(post["excerpt"]),
        canonical="%s/blog/%s/" % (SITE, post["slug"]),
        og_image=image,
        og_image_alt=attr(post.get("image_alt")
                          or "Talon Construction Company, Penn Valley, California"),
        og_type="article",
        extra_meta=(
            '  <meta name="author" content="Talon Construction Company">\n'
            '  <meta property="article:published_time" content="%s">\n'
            '  <meta property="article:modified_time" content="%s">\n'
            % (post["date"], modified)
            + ('  <meta property="article:section" content="%s">\n'
               % attr(post["tag"]) if post.get("tag") else "")
        ),
        schema=schema,
    )

    return head + """
    <article class="post">
      <div class="wrap wrap-reading">
        <p class="post-back"><a href="/blog/">&larr; The Journal</a></p>
        <h1>{title}</h1>
        <p class="post-meta">{meta}</p>
      </div>
      {figure}
      <div class="wrap wrap-reading post-body">
{body}
      </div>
      <div class="wrap wrap-reading">
        <nav class="post-nav" aria-label="More posts">{nav}</nav>
        <aside class="post-cta">
          <h2>Thinking about a project?</h2>
          <p>Talon has been building in Nevada County since 1981. Tell us what you have in mind and we will talk it through.</p>
          <a class="btn btn-gold" href="/#contact">Start Your Project</a>
        </aside>
      </div>
    </article>
""".format(
        title=esc(post["title"]),
        meta=" ".join(meta),
        figure=figure(post, "wide"),
        body=body,
        nav="\n          ".join(nav),
    ) + FOOT


def archive_page():
    if not posts:
        # Honest empty state. Better than a page of nothing, and it makes the
        # pipeline visibly working before any content exists.
        inner = """
    <section class="page-intro">
      <div class="wrap wrap-reading">
        <h1>The Journal</h1>
        <p>Notes from the job site &mdash; what we are building around Nevada County, and what we have learned doing it.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap wrap-reading">
        <p class="blog-empty">The first posts are being written. In the meantime, the quickest way to get an answer about your project is to ask us directly.</p>
        <p><a class="btn btn-gold" href="/#contact">Start Your Project</a></p>
      </div>
    </section>
"""
    else:
        used = [t for t in tags if any(p.get("tag") == t for p in posts)]
        filters = ""
        if len(used) > 1:
            # Only worth showing when there is something to filter BETWEEN.
            buttons = "".join(
                '<button type="button" class="blog-filter" data-filter="%s">%s</button>'
                % (attr(t), esc(t)) for t in used
            )
            filters = (
                '<div class="blog-filters" id="blogFilters" hidden>'
                '<button type="button" class="blog-filter is-active" data-filter="*">All</button>'
                + buttons + "</div>"
            )

        cards = []
        for p in posts:
            bits = ['<span class="post-date">%s</span>' % pretty_date(p["date"])]
            if p.get("tag"):
                bits.append('<span class="post-tag">%s</span>' % esc(p["tag"]))
            cards.append("""      <li class="post-card" data-tag="{tag}">
        <a class="post-card-link" href="/blog/{slug}/">
          {figure}
          <div class="post-card-body">
            <p class="post-card-meta">{meta}</p>
            <h2>{title}</h2>
            <p class="post-card-excerpt">{excerpt}</p>
            <span class="post-card-more">Read the post &rarr;</span>
          </div>
        </a>
      </li>""".format(
                tag=attr(p.get("tag", "")),
                slug=p["slug"],
                figure=figure(p, "card"),
                meta=" ".join(bits),
                title=esc(p["title"]),
                excerpt=esc(p["excerpt"]),
            ))

        inner = """
    <section class="page-intro">
      <div class="wrap wrap-reading">
        <h1>The Journal</h1>
        <p>Notes from the job site &mdash; what we are building around Nevada County, and what we have learned doing it.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap">
        {filters}
        <ul class="post-grid" id="postGrid">
{cards}
        </ul>
        <p class="blog-no-results" id="blogNoResults" hidden>Nothing in that category yet.</p>
      </div>
    </section>
""".format(filters=filters, cards="\n".join(cards))

    # blog.js only ships on the archive - the post pages have nothing to filter.
    # blog.js ships only on the archive - a post page has nothing to filter.
    inner += '    <script src="/js/blog.js?v=1" defer></script>' + chr(10)

    head = HEAD.format(
        title="The Journal | Talon Construction Company",
        description="Notes from the job site - custom home building, remodels and additions around Penn Valley, Grass Valley, Nevada City and the wider Nevada County area.",
        canonical="%s/blog/" % SITE,
        og_image="%s/assets/hero-1920.jpg" % SITE,
        og_image_alt="Talon Construction Company, Penn Valley, California",
        og_type="website",
        extra_meta="",
        schema=ld(
            {
                "@context": "https://schema.org",
                "@type": "Blog",
                "@id": "%s/blog/#journal" % SITE,
                "name": "The Journal",
                "description": "Notes from the job site - custom home building, "
                               "remodels and additions around Nevada County.",
                "url": "%s/blog/" % SITE,
                "inLanguage": "en-US",
                "publisher": org_node(),
                "blogPost": [
                    {"@type": "BlogPosting",
                     "headline": p["title"],
                     "datePublished": p["date"],
                     "url": "%s/blog/%s/" % (SITE, p["slug"])}
                    for p in posts
                ],
            },
            crumbs([("Home", SITE + "/"), ("The Journal", "%s/blog/" % SITE)]),
        ),
    )
    return head + inner + FOOT


# --- write -------------------------------------------------------------
blog = ROOT / "blog"
blog.mkdir(exist_ok=True)
(blog / "index.html").write_text(archive_page(), encoding="utf-8", newline="\n")

for i, p in enumerate(posts):
    newer = posts[i - 1] if i > 0 else None
    older = posts[i + 1] if i + 1 < len(posts) else None
    d = blog / p["slug"]
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(post_page(p, newer, older), encoding="utf-8", newline="\n")

# Remove pages for posts that were deleted from the JSON, so an unpublished
# post does not linger at a live URL.
keep = {p["slug"] for p in posts}
orphans = [d for d in blog.iterdir() if d.is_dir() and d.name not in keep]
stuck = []
for d in orphans:
    for f in d.iterdir():
        try:
            f.unlink()
        except OSError as err:
            stuck.append("%s (%s)" % (f, err))
    try:
        d.rmdir()
    except OSError as err:
        # Windows will refuse this while anything holds the directory open -
        # a local preview server, an editor, a virus scanner. The page file is
        # already gone, so the URL is dead either way; an empty directory left
        # behind is untidy, not dangerous. Warn, do not abort the build.
        stuck.append("%s (%s)" % (d, err))

print("%d post(s) written to /blog/" % len(posts))
if orphans:
    print("removed %d orphaned page(s): %s" % (len(orphans), ", ".join(d.name for d in orphans)))
if stuck:
    print("WARNING - could not fully remove %d path(s); the page files are gone" % len(stuck))
    print("but empty directories remain. Close any local preview server and re-run.")
    for s in stuck:
        print("  " + s)
if not posts:
    print("posts.json is empty - /blog renders its empty state, and build-sitemap.py")
    print("will leave the blog out of the sitemap until a post exists.")
