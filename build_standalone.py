#!/usr/bin/env python3
"""Wrap the concept study into a standalone, self-hostable page.

front-porch-village.html is authored as a body fragment (it carries its own
<title>, <link> and <style> but no document skeleton). This lifts the head
elements into a real <head>, adds the robots directives, and writes site/,
which can be dropped onto any static host as-is.

    python3 build_standalone.py
"""

import pathlib
import re

HERE = pathlib.Path(__file__).parent
SRC = HERE / "front-porch-village.html"
OUT_DIR = HERE / "site"

DESCRIPTION = (
    "An interactive 3D concept study for a transitional housing non-profit: three tiny homes with "
    "deep front porches around a shared green, for young adults aging out of "
    "foster care."
)

# Matches the minimal reset the page was authored against, so the standalone
# build renders identically to the preview it was tuned in.
RESET = """    :root{color-scheme:light}
    body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif;background:#faf9f7}
    img{max-width:100%}
    [hidden]{display:none!important}"""


def build() -> None:
    src = SRC.read_text(encoding="utf-8")

    title_match = re.search(r"<title>(.*?)</title>", src, re.S)
    if not title_match:
        raise SystemExit("source has no <title>")
    title = title_match.group(1).strip()

    links = re.findall(r"<link [^>]*>", src)

    body = re.sub(r"<title>.*?</title>\s*", "", src, count=1, flags=re.S)
    for link in links:
        body = body.replace(link + "\n", "", 1)
    body = body.lstrip("\n")

    head_links = "\n".join("  " + link for link in links)

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

  <!-- Not for search engines: this is a working draft shared by link only. -->
  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
  <meta name="googlebot" content="noindex, nofollow">
  <meta name="referrer" content="strict-origin-when-cross-origin">

  <title>{title}</title>
  <meta name="description" content="{DESCRIPTION}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} — concept study">
  <meta property="og:description" content="{DESCRIPTION}">

{head_links}
  <style>
{RESET}
  </style>
</head>
<body>
{body}</body>
</html>
"""

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")

    # Belt and braces: a crawler that ignores the meta tag still gets told here,
    # and hosts that read _headers send the directive as an HTTP header.
    (OUT_DIR / "robots.txt").write_text(
        "User-agent: *\nDisallow: /\n", encoding="utf-8"
    )
    (OUT_DIR / "_headers").write_text(
        "/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n", encoding="utf-8"
    )

    kb = (OUT_DIR / "index.html").stat().st_size / 1024
    print(f"wrote {OUT_DIR/'index.html'} ({kb:.0f} KB), robots.txt, _headers")


if __name__ == "__main__":
    build()
