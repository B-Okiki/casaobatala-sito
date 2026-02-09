#!/usr/bin/env python3
"""
Script per convertire gli articoli Markdown in HTML
Casa Obàtálá - Blog Builder

Changelog rispetto alla versione originale:
- Fix: rimozione backslash da CMS (Sveltia/Decap) prima della conversione MD→HTML
- Fix: liste ordinate wrappate in <ol>
- Fix: liste separate correttamente (non fuse in un unico blocco)
- Fix: horizontal rule non confligge col frontmatter
- Fix: parsing date robusto (datetime, date, stringhe varie)
- Fix: troncamento descrizione senza spezzare parole
- Fix: coerenza path immagini tra articolo e index
- Fix: pulizia titoli (rimozione # iniziali da Decap CMS)
- Fix: tag vuoti filtrati, duplicati rimossi, URL-encoded nei link
- Fix: reading time calcolato su testo pulito
- Miglioramento: marker contenuto dedicati con fallback a cascata
- Miglioramento: log errori YAML
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# Cartelle
BLOG_FOLDER = "blog"
TEMPLATE_FILE = "templates/articolo-blog-template.html"
OUTPUT_FOLDER = "blog"

# Marker per il template
CONTENT_MARKER_START = "<!-- CONTENT_START -->"
CONTENT_MARKER_END = "<!-- CONTENT_END -->"

# Mappa categorie per visualizzazione
CATEGORIE = {
    "meditazione": "Meditazione",
    "piante": "Piante e Fitoterapia",
    "yoruba": "Tradizione Yoruba",
    "orisa": "Òrìṣà",
    "crescita": "Crescita Personale",
    "riflessioni": "Riflessioni"
}


# ============================================
# PARSING
# ============================================

def parse_frontmatter(content):
    """Estrae i metadati YAML dall'inizio del file markdown."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata, body
            except yaml.YAMLError as e:
                print(f"  ⚠️  Errore parsing YAML: {e}")
    return {}, content


def clean_title(title):
    """Rimuove # iniziali e spazi extra dai titoli (artefatto di Decap CMS)."""
    return re.sub(r'^#+\s*', '', title).strip()


def parse_date(date_obj):
    """Normalizza una data dal frontmatter in un oggetto datetime."""
    if isinstance(date_obj, datetime):
        return date_obj
    if hasattr(date_obj, 'year'):  # date object (da YAML)
        return datetime(date_obj.year, date_obj.month, date_obj.day)
    date_str = str(date_obj).strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except ValueError:
        print(f"  ⚠️  Formato data non riconosciuto: '{date_str}', uso data odierna")
        return datetime.now()


def format_date_italian(date_input):
    """Formatta la data in italiano."""
    mesi = {
        1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
        5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
        9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
    }
    date_obj = parse_date(date_input)
    return f"{date_obj.day} {mesi[date_obj.month]} {date_obj.year}"


def parse_tags(raw_tags):
    """Normalizza i tag: gestisce stringhe e liste con virgole.
    Rimuove punti finali, spazi extra e duplicati."""
    if isinstance(raw_tags, str):
        tags = [t.strip().rstrip('.') for t in raw_tags.split(',') if t.strip()]
    elif isinstance(raw_tags, list):
        expanded = []
        for tag in raw_tags:
            expanded.extend([t.strip().rstrip('.') for t in str(tag).split(',')])
        tags = [t for t in expanded if t]
    else:
        tags = []
    # Deduplica preservando ordine
    seen = set()
    unique = []
    for t in tags:
        t_lower = t.lower()
        if t_lower not in seen:
            seen.add(t_lower)
            unique.append(t)
    return unique


def truncate_text(text, max_length=150):
    """Tronca il testo senza spezzare parole."""
    if not text or len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated + "…"


# ============================================
# CONVERSIONE MARKDOWN → HTML
# ============================================

def strip_cms_backslashes(text):
    r"""Rimuove i backslash inseriti da Sveltia/Decap CMS davanti
    alla sintassi markdown (es. \* → *, \_ → _)."""
    text = re.sub(r'\\(\*)', r'\1', text)
    text = re.sub(r'\\(_)', r'\1', text)
    text = re.sub(r'\\(#)', r'\1', text)
    text = re.sub(r'\\(\[)', r'\1', text)
    text = re.sub(r'\\(\])', r'\1', text)
    text = re.sub(r'\\(\()', r'\1', text)
    text = re.sub(r'\\(\))', r'\1', text)
    return text


def markdown_to_html(text):
    """Converte markdown base in HTML."""
    # STEP 0: Rimuovi backslash da CMS
    text = strip_cms_backslashes(text)

    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)

    # Bold e italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\w)\*([^*\n]+?)\*(?!\w)', r'<em>\1</em>', text)

    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Images
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', text)

    # Horizontal rules (prima dei blockquote)
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '<hr>', text, flags=re.MULTILINE)

    # Blockquotes
    lines = text.split('\n')
    in_blockquote = False
    new_lines = []
    for line in lines:
        if line.startswith('> '):
            if not in_blockquote:
                new_lines.append('<blockquote>')
                in_blockquote = True
            new_lines.append(line[2:])
        else:
            if in_blockquote:
                new_lines.append('</blockquote>')
                in_blockquote = False
            new_lines.append(line)
    if in_blockquote:
        new_lines.append('</blockquote>')
    text = '\n'.join(new_lines)

    # Liste non ordinate
    text = _wrap_list_items(text, prefix=r'^- ', tag='ul')

    # Liste ordinate
    text = _wrap_list_items(text, prefix=r'^\d+\. ', tag='ol')

    # Paragrafi
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        new_paragraphs.append(p)
    text = '\n\n'.join(new_paragraphs)

    # Pulisci newlines dentro i paragrafi
    text = re.sub(
        r'<p>(.+?)</p>',
        lambda m: '<p>' + m.group(1).replace('\n', ' ') + '</p>',
        text,
        flags=re.DOTALL
    )

    return text


def _wrap_list_items(text, prefix, tag):
    """Raggruppa righe consecutive matchanti in blocchi <tag>...</tag>."""
    lines = text.split('\n')
    result = []
    in_list = False

    for line in lines:
        is_item = re.match(prefix, line)
        if is_item:
            item_text = re.sub(prefix, '', line)
            if not in_list:
                result.append(f'<{tag}>')
                in_list = True
            result.append(f'<li>{item_text}</li>')
        else:
            if in_list:
                result.append(f'</{tag}>')
                in_list = False
            result.append(line)

    if in_list:
        result.append(f'</{tag}>')

    return '\n'.join(result)


def calculate_reading_time(text):
    """Calcola tempo di lettura (200 parole/minuto) su testo pulito."""
    clean = strip_cms_backslashes(text)
    clean = re.sub(r'[#*\[\]()!`>]', '', clean)
    clean = re.sub(r'\{[^}]+\}', '', clean)
    words = len(clean.split())
    minutes = max(1, round(words / 200))
    return minutes


# ============================================
# BUILD ARTICOLI
# ============================================

def build_article(md_file, template):
    """Costruisce l'HTML di un articolo dal file markdown."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata, body = parse_frontmatter(content)

    if not metadata:
        print(f"  ⚠️  Nessun frontmatter trovato: {md_file}")
        return None

    if not metadata.get('published', False):
        print(f"  ⏭️  Saltato (bozza): {md_file}")
        return None

    body_html = markdown_to_html(body)

    title = clean_title(metadata.get('title', 'Senza titolo'))
    date_obj = parse_date(metadata.get('date', datetime.now()))
    date_str = date_obj.strftime("%Y-%m-%d")

    category_key = metadata.get('category', 'riflessioni')
    category_display = CATEGORIE.get(category_key, category_key.title())

    description = metadata.get('description', '')
    image = metadata.get('image', '')
    image_alt = metadata.get('image_alt', title)
    tags = parse_tags(metadata.get('tags', []))

    slug = Path(md_file).stem
    reading_time = calculate_reading_time(body)

    image_filename = image.replace('/images/blog/', '') if image else ''

    tags_html = ' '.join(
        [f'<a href="/blog.html?tag={quote(tag)}" class="tag">{tag}</a>'
         for tag in tags if tag]
    )

    html = template

    replacements = {
        '{{TITOLO_ARTICOLO}}': title,
        '{{DESCRIZIONE_SEO}}': description,
        '{{SLUG_ARTICOLO}}': slug,
        '{{DATA_ISO}}': date_str,
        '{{DATA_FORMATTATA}}': format_date_italian(date_obj),
        '{{CATEGORIA}}': category_display,
        '{{MINUTI_LETTURA}}': str(reading_time),
        '{{IMMAGINE_ARTICOLO}}': image_filename if image_filename else 'placeholder.jpg',
        '{{ALT_IMMAGINE}}': image_alt,
        '{{DIDASCALIA_IMMAGINE}}': '',
        '{{TAGS_SEPARATI_DA_VIRGOLA}}': ', '.join(tags) if tags else '',
        '{{TAGS_HTML}}': tags_html,
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # ---- Inserimento contenuto (3 strategie con fallback) ----
    if CONTENT_MARKER_START in html and CONTENT_MARKER_END in html:
        before = html.split(CONTENT_MARKER_START)[0]
        after = html.split(CONTENT_MARKER_END)[1]
        html = before + CONTENT_MARKER_START + '\n' + body_html + '\n' + CONTENT_MARKER_END + after
    else:
        legacy_start = "<!-- ============================================\n                 QUI VA IL CONTENUTO DELL'ARTICOLO"
        legacy_end = '<!-- Fine contenuto -->'
        if legacy_start in html and legacy_end in html:
            before = html.split(legacy_start)[0]
            after = html.split(legacy_end)[1]
            html = before + body_html + '\n            ' + legacy_end + after
        else:
            match = re.search(r'(<div class="article-content">)', html)
            if match:
                insert_pos = match.end()
                html = html[:insert_pos] + '\n' + body_html + '\n' + html[insert_pos:]
                print(f"  ⚠️  Usato fallback generico per: {md_file}")
            else:
                print(f"  ❌ Impossibile inserire contenuto: {md_file}")
                return None

    # Gestisci immagine mancante
    if not image:
        html = re.sub(
            r'<figure class="featured-image">.*?</figure>',
            '',
            html,
            flags=re.DOTALL
        )

    # Rimuovi sezione articoli correlati vuota
    html = re.sub(
        r'<section class="related-articles">.*?</section>',
        '',
        html,
        flags=re.DOTALL
    )

    # Pulisci placeholder rimanenti
    html = re.sub(r'\{\{[^}]+\}\}', '', html)

    return html


# ============================================
# INDICE BLOG
# ============================================

def update_blog_index(articles):
    """Aggiorna blog.html con la lista degli articoli."""
    blog_file = "blog.html"

    if not os.path.exists(blog_file):
        print("  ⚠️  blog.html non trovato")
        return

    with open(blog_file, 'r', encoding='utf-8') as f:
        html = f.read()

    cards_html = ""
    for article in sorted(articles, key=lambda x: x['date'], reverse=True):
        if article['image']:
            image_html = (
                f'<img src="{article["image"]}" alt="{article["image_alt"]}" '
                f'class="blog-card-image">'
            )
        else:
            image_html = '<div class="blog-card-image"></div>'

        description_safe = truncate_text(article['description'])

        cards_html += f'''
        <a href="blog/{article['slug']}.html" class="blog-card">
            {image_html}
            <div class="blog-card-content">
                <span class="blog-card-category">{article['category']}</span>
                <h2>{article['title']}</h2>
                <p>{description_safe}</p>
                <div class="blog-card-meta">
                    <span>📅 {article['date_formatted']}</span>
                    <span class="read-more">Leggi →</span>
                </div>
            </div>
        </a>
'''

    if not cards_html:
        cards_html = '''
        <div class="empty-state">
            <h3>🌱 Prossimamente</h3>
            <p>Il blog è in arrivo. Iscriviti per ricevere notifiche sui nuovi articoli.</p>
            <a href="contatti.html" style="display: inline-block; margin-top: 1.5rem; padding: 0.8rem 1.5rem; background: linear-gradient(135deg, #8B4513, #A0522D); color: white; text-decoration: none; border-radius: 25px; font-size: 0.85rem;">Contattami</a>
        </div>
'''

    html = re.sub(
        r'(<div class="blog-grid">).*?(</div>\s*<div class="button-container">)',
        f'\\1{cards_html}\n    \\2',
        html,
        flags=re.DOTALL
    )

    with open(blog_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  ✅ blog.html aggiornato con {len(articles)} articoli")


# ============================================
# MAIN
# ============================================

def main():
    print("🔨 Build Blog - Casa Obàtálá")
    print("=" * 40)

    if not os.path.exists(BLOG_FOLDER):
        print(f"❌ Cartella {BLOG_FOLDER}/ non trovata")
        return

    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Template {TEMPLATE_FILE} non trovato")
        return

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    md_files = list(Path(BLOG_FOLDER).glob("*.md"))
    print(f"📄 Trovati {len(md_files)} file markdown")

    articles = []

    for md_file in md_files:
        print(f"  📝 Processo: {md_file.name}")

        html = build_article(str(md_file), template)

        if html:
            output_file = md_file.with_suffix('.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  ✅ Creato: {output_file.name}")

            with open(md_file, 'r', encoding='utf-8') as f:
                metadata, _ = parse_frontmatter(f.read())

            date_obj = parse_date(metadata.get('date', datetime.now()))
            date_str = date_obj.strftime("%Y-%m-%d")

            articles.append({
                'slug': md_file.stem,
                'title': clean_title(metadata.get('title', 'Senza titolo')),
                'description': metadata.get('description', ''),
                'date': date_str,
                'date_formatted': format_date_italian(date_obj),
                'category': CATEGORIE.get(metadata.get('category', ''), 'Riflessioni'),
                'image': metadata.get('image', ''),
                'image_alt': metadata.get('image_alt', ''),
            })

    print(f"\n📋 Aggiorno indice blog...")
    update_blog_index(articles)

    print(f"\n✨ Build completata! ({len(articles)} articoli pubblicati)")


if __name__ == "__main__":
    main()
