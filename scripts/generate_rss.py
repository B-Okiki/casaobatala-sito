#!/usr/bin/env python3
"""
Generatore Feed RSS - Casa Obàtálá

Legge i file Markdown del blog (stessa cartella usata da build_blog.py),
estrae il front matter YAML e genera un feed RSS 2.0 valido.

Va eseguito DOPO build_blog.py, così i file HTML sono già generati.

Uso:
    python scripts/generate_rss.py

Output:
    feed.xml nella root del repository

Nessuna dipendenza esterna (usa solo librerie standard Python).
Se pyyaml è disponibile lo usa, altrimenti parsa il front matter manualmente.
"""

import os
import re
import html
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path

# Configurazione
SITE_URL = "https://casaobatala.it"
SITE_TITLE = "Casa Obàtálá - Blog"
SITE_DESCRIPTION = "Tradizione Yoruba, spiritualità, meditazione e piante sacre. Il blog di Lorenzo Okìkí Rossi."
SITE_LANGUAGE = "it"
BLOG_DIR = "blog"
OUTPUT_FILE = "feed.xml"
MAX_ITEMS = 20  # Numero massimo di articoli nel feed


def parse_front_matter(filepath):
    """Estrae il front matter YAML da un file Markdown.
    
    Supporta sia pyyaml (se installato) sia parsing manuale
    per i campi essenziali.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Cerca il front matter delimitato da ---
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return None, content

    fm_text = match.group(1)
    body = match.group(2)

    # Prova con pyyaml
    try:
        import yaml
        fm = yaml.safe_load(fm_text)
        if isinstance(fm, dict):
            return fm, body
    except ImportError:
        pass

    # Fallback: parsing manuale dei campi essenziali
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                fm[key] = value

    return fm, body


def get_blog_posts():
    """Trova e parsa tutti i post del blog, ordinati per data (più recenti prima)."""
    posts = []

    if not os.path.exists(BLOG_DIR):
        print(f"⚠️  Cartella {BLOG_DIR} non trovata")
        return posts

    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(BLOG_DIR, filename)
        fm, body = parse_front_matter(filepath)

        if not fm:
            continue

        # Salta bozze
        if fm.get("draft", False) in (True, "true", "True"):
            continue

        # Costruisci l'URL della pagina HTML
        # Il tuo build_blog.py genera file come:
        # blog/2026-02-05-titolo.md → blog/2026-02-05-titolo.html
        html_filename = filename.replace(".md", ".html")
        url = f"{SITE_URL}/blog/{html_filename}"

        # Data
        date_str = str(fm.get("date", ""))
        try:
            if "T" in date_str:
                pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                pub_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except (ValueError, IndexError):
            # Prova a estrarre la data dal nome del file
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
            if date_match:
                pub_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            else:
                pub_date = datetime.now()

        # Descrizione: usa il campo description/excerpt del front matter
        # oppure i primi ~200 caratteri del body
        description = fm.get("description", "") or fm.get("excerpt", "")
        if not description:
            # Rimuovi markup markdown e prendi i primi 200 caratteri
            clean_body = re.sub(r"[#*\[\]()!`>]", "", body)
            clean_body = re.sub(r"\n+", " ", clean_body).strip()
            description = clean_body[:200] + "..." if len(clean_body) > 200 else clean_body

        # Immagine (per Open Graph / enclosure)
        image = fm.get("image", "") or fm.get("thumbnail", "") or fm.get("cover", "")
        if image and not image.startswith("http"):
            image = f"{SITE_URL}/{image.lstrip('/')}"

        # Categorie/tag
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]

        posts.append({
            "title": fm.get("title", filename),
            "url": url,
            "date": pub_date,
            "description": description,
            "image": image,
            "tags": tags,
            "author": fm.get("author", "Lorenzo Okìkí Rossi"),
        })

    # Ordina per data (più recenti prima)
    posts.sort(key=lambda p: p["date"], reverse=True)

    return posts[:MAX_ITEMS]


def escape_xml(text):
    """Escape caratteri speciali per XML."""
    return html.escape(str(text), quote=True)


def generate_rss(posts):
    """Genera il contenuto XML del feed RSS 2.0."""
    now = format_datetime(datetime.now())

    items = []
    for post in posts:
        # Formatta data in RFC 2822 (standard RSS)
        try:
            pub_date = format_datetime(post["date"])
        except (TypeError, ValueError):
            pub_date = now

        # Categorie
        categories = ""
        for tag in post.get("tags", []):
            if tag:
                categories += f"      <category>{escape_xml(tag)}</category>\n"

        # Enclosure (immagine)
        enclosure = ""
        if post.get("image"):
            enclosure = f'      <enclosure url="{escape_xml(post["image"])}" type="image/jpeg" />\n'

        item = f"""    <item>
      <title>{escape_xml(post['title'])}</title>
      <link>{escape_xml(post['url'])}</link>
      <guid isPermaLink="true">{escape_xml(post['url'])}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{escape_xml(post['description'])}</description>
      <author>{escape_xml(post['author'])}</author>
{categories}{enclosure}    </item>"""
        items.append(item)

    items_xml = "\n".join(items)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{escape_xml(SITE_TITLE)}</title>
    <link>{SITE_URL}</link>
    <description>{escape_xml(SITE_DESCRIPTION)}</description>
    <language>{SITE_LANGUAGE}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
    <image>
      <url>{SITE_URL}/favicon-96x96.png</url>
      <title>{escape_xml(SITE_TITLE)}</title>
      <link>{SITE_URL}</link>
    </image>
{items_xml}
  </channel>
</rss>"""

    return rss


def main():
    print("📡 Generatore RSS - Casa Obàtálá")
    print("=" * 40)

    posts = get_blog_posts()
    print(f"📄 Articoli trovati: {len(posts)}")

    if not posts:
        print("ℹ️  Nessun articolo trovato, feed vuoto generato")

    for post in posts:
        date_str = post["date"].strftime("%Y-%m-%d")
        print(f"   → [{date_str}] {post['title']}")

    rss_content = generate_rss(posts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_content)

    print(f"\n✅ Feed RSS generato: {OUTPUT_FILE}")
    print(f"   URL: {SITE_URL}/feed.xml")
    print(f"\n✨ Completato!")


if __name__ == "__main__":
    main()
