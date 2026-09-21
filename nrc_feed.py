#!/usr/bin/env python3
"""Voegt vier NRC-rubrieksfeeds samen tot één ontdubbelde RSS-feed.

Haalt de feeds van Binnenland, Buitenland, Economie en Den Haag op,
ontdubbelt op guid, en schrijft het resultaat naar docs/feed.xml.
Eerder-gezien tijdstippen worden onthouden in seen.json zodat
publicatiedatums stabiel blijven.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

# (rubriek, url, alleen items met deze <category> of None voor alles)
FEEDS = [
    ("Binnenland",    "https://www.nrc.nl/index/binnenland/rss/", None),
    ("Buitenland",    "https://www.nrc.nl/index/buitenland/rss/", None),
    ("Economie",      "https://www.nrc.nl/index/economie/rss/", None),
    ("Den Haag",      "https://www.nrc.nl/index/den-haag/rss/", None),
    # De hoofdartikelen bovenaan nrc.nl dragen in de voorpaginafeed de categorie "Vandaag".
    ("Voorpagina",    "https://www.nrc.nl/rss/", "Vandaag"),
    ("Beste van NRC", "https://www.nrc.nl/index/home/beste-van-nrc/rss/", None),
]

USER_AGENT = "nrc-rss/1.0 (github.com/sietse88/nrc-rss)"
OUTPUT = Path("docs/feed.xml")
SEEN_FILE = Path("seen.json")
SEEN_RETENTION_DAYS = 14
REQUEST_PAUSE = 0.5

SITE_BASE_URL = "https://sietse88.github.io/nrc-rss"
FEED_ICON_URL = f"{SITE_BASE_URL}/icon.png"


def fetch_feed(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return ET.parse(r).getroot()


def parse_items(root, section, only_category=None):
    items = []
    channel = root.find("channel")
    if channel is None:
        return items
    for el in channel.findall("item"):
        guid = (el.findtext("guid") or "").strip()
        if not guid:
            continue
        if only_category and (el.findtext("category") or "").strip() != only_category:
            continue

        enc_el = el.find("enclosure")
        enclosure = None
        if enc_el is not None:
            enclosure = {
                "url": enc_el.get("url", ""),
                "length": enc_el.get("length", "0"),
                "type": enc_el.get("type", ""),
            }

        items.append({
            "guid": guid,
            "title": (el.findtext("title") or "").strip(),
            "link": (el.findtext("link") or "").strip(),
            "pubDate": (el.findtext("pubDate") or "").strip(),
            "description": (el.findtext("description") or "").strip(),
            "enclosure": enclosure,
            "categories": {section},
        })
    return items


def load_seen():
    if not SEEN_FILE.exists():
        return {}
    try:
        return json.loads(SEEN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_seen(seen):
    SEEN_FILE.write_text(
        json.dumps(seen, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def is_recent(rfc_date, cutoff):
    try:
        dt = parsedate_to_datetime(rfc_date)
    except (TypeError, ValueError):
        return True
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt >= cutoff


def parse_pub_date(s):
    try:
        dt = parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def esc_attr(s):
    return escape(s, {'"': "&quot;"})


def build_rss(items, now):
    rss_items = []
    for it in items:
        parts = [
            "  <item>",
            f"    <title>{escape(it['title'])}</title>",
            f"    <link>{escape(it['link'])}</link>",
            f"    <guid isPermaLink=\"false\">{escape(it['guid'])}</guid>",
            f"    <pubDate>{it['pubDate']}</pubDate>",
            f"    <description>{escape(it['description'])}</description>",
        ]
        if it.get("enclosure"):
            enc = it["enclosure"]
            parts.append(
                f"    <enclosure url=\"{esc_attr(enc['url'])}\""
                f" length=\"{esc_attr(enc['length'])}\""
                f" type=\"{esc_attr(enc['type'])}\"/>"
            )
        for cat in it.get("categories", []):
            parts.append(f"    <category>{escape(cat)}</category>")
        parts.append("  </item>")
        rss_items.append("\n".join(parts))

    body = "\n".join(rss_items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "<channel>\n"
        "  <title>NRC</title>\n"
        "  <link>https://www.nrc.nl/</link>\n"
        "  <description>NRC — voorpagina, Beste van NRC, Binnenland, Buitenland,"
        " Economie en Den Haag in \xe9\xe9n feed, zonder dubbele artikelen.</description>\n"
        "  <language>nl-NL</language>\n"
        "  <image>\n"
        f"    <url>{escape(FEED_ICON_URL)}</url>\n"
        "    <title>NRC</title>\n"
        "    <link>https://www.nrc.nl/</link>\n"
        "  </image>\n"
        f"  <lastBuildDate>{format_datetime(now)}</lastBuildDate>\n"
        f"{body}\n"
        "</channel>\n"
        "</rss>\n"
    )


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    seen = load_seen()
    now = datetime.now(timezone.utc)
    now_str = format_datetime(now)

    merged = {}
    total = 0
    for section, url, only_category in FEEDS:
        try:
            root = fetch_feed(url)
        except (urllib.error.URLError, ET.ParseError) as e:
            print(f"Feed {section} overgeslagen: {e}", file=sys.stderr)
            continue
        items = parse_items(root, section, only_category)
        total += len(items)
        for it in items:
            guid = it["guid"]
            if guid in merged:
                merged[guid]["categories"] |= it["categories"]
            else:
                merged[guid] = it
        print(f"  {section}: {len(items)} artikelen")
        time.sleep(REQUEST_PAUSE)

    if not merged:
        print("Geen artikelen gevonden.", file=sys.stderr)
        return 1

    for guid, it in merged.items():
        entry = seen.get(guid)
        if entry:
            it["pubDate"] = entry["first"]
            seen[guid]["last"] = now_str
        else:
            seen[guid] = {"first": it["pubDate"], "last": now_str}

    items_list = sorted(
        merged.values(),
        key=lambda it: parse_pub_date(it["pubDate"]) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    for it in items_list:
        it["categories"] = sorted(it["categories"])

    cutoff = now - timedelta(days=SEEN_RETENTION_DAYS)
    seen = {g: v for g, v in seen.items() if is_recent(v["last"], cutoff)}
    save_seen(seen)

    OUTPUT.write_text(build_rss(items_list, now), encoding="utf-8")
    dupes = total - len(merged)
    print(f"Geschreven: {OUTPUT} ({len(merged)} artikelen, {dupes} dubbele verwijderd)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
