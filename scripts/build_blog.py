#!/usr/bin/env python3
"""
Script per convertire gli articoli Markdown in HTML
Casa Obàtálá - Blog Builder
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path

# Cartelle
BLOG_FOLDER = "blog"
TEMPLATE_FILE = "templates/articolo-blog-template.html"
OUTPUT_FOLDER = "blog"

# Mappa categorie per visualizzazione
CATEGORIE = {
    "meditazione": "Meditazione",
    "piante": "Piante e Fitoterapia",
    "yoruba": "Tradizione Yoruba",
    "orisa": "Òrìṣà",
    "crescita": "Crescita Personale",
    "riflessioni": "Riflessioni"
}

def parse_frontmatter(content):
    """Estrae i metadati YAML dall'inizio del file markdown."""
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return metadata, body
            except yaml.YAMLError:
                pass
    return {}, content

def markdown_to_html(text):
    """Converte markdown base in HTML."""
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    
    # Bold e italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    # Images
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', text)
    
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
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*</li>\n?)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', text)
    
    # Liste ordinate
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
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
    text = re.sub(r'<p>(.+?)</p>', lambda m: '<p>' + m.group(1).replace('\n', ' ') + '</p>', text, flags=re.DOTALL)
    
    # Horizontal rules
    text = re.sub(r'^---+$', '<hr>', text, flags=re.MULTILINE)
    
    return text

def calculate_reading_time(text):
    """Calcola tempo di lettura (200 parole/minuto)."""
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return minutes

def format_date_italian(date_obj):
    """Formatta la data in italiano."""
    mesi = {
        1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
        5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
        9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
    }
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
    return f"{date_obj.day} {mesi[date_obj.month]} {date_obj.year}"

def build_article(md_file, template):
    """Costruisce l'HTML di un articolo dal file markdown."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata, body = parse_frontmatter(content)
    
    # Verifica se pubblicato
    if not metadata.get('published', False):
        print(f"  ⏭️  Saltato (bozza): {md_file}")
        return None
    
    # Converti markdown in HTML
    body_html = markdown_to_html(body)
    
    # Prepara i dati
    title = metadata.get('title', 'Senza titolo')
    date = metadata.get('date', datetime.now().strftime("%Y-%m-%d"))
    tags = metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',')]
    else:
        # Gestisce il caso Sveltia: lista con un singolo elemento separato da virgole
        expanded = []
        for tag in tags:
            expanded.extend([t.strip() for t in str(tag).split(',')])
        tags = [t for t in expanded if t]
    
    category_key = metadata.get('category', 'riflessioni')
    category_display = CATEGORIE.get(category_key, category_key.title())
    
    description = metadata.get('description', '')
    image = metadata.get('image', '')
    image_alt = metadata.get('image_alt', title)
    tags = metadata.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',')]
    
    # Slug dal nome file
    slug = Path(md_file).stem
    
    # Tempo di lettura
    reading_time = calculate_reading_time(body)
    
    # Costruisci HTML
    html = template
    
    # Sostituzioni base
    replacements = {
        '{{TITOLO_ARTICOLO}}': title,
        '{{DESCRIZIONE_SEO}}': description,
        '{{SLUG_ARTICOLO}}': slug,
        '{{DATA_ISO}}': date_str,
        '{{DATA_FORMATTATA}}': format_date_italian(date_str),
        '{{CATEGORIA}}': category_display,
        '{{MINUTI_LETTURA}}': str(reading_time),
        '{{IMMAGINE_ARTICOLO}}': image.replace('/images/blog/', '') if image else 'placeholder.jpg',
        '{{ALT_IMMAGINE}}': image_alt,
        '{{DIDASCALIA_IMMAGINE}}': '',
        '{{TAGS_SEPARATI_DA_VIRGOLA}}': ', '.join(tags) if tags else '',
    }
    
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    # Tags singoli
    for i, tag in enumerate(tags[:3], 1):
        html = html.replace(f'{{{{TAG{i}}}}}', tag)
    
    # Rimuovi placeholder tag non usati
    html = re.sub(r'\{\{TAG\d+\}\}', '', html)
    
    # Sostituisci il contenuto principale
    # Trova la sezione del contenuto e sostituiscila
    content_start = '<!-- ============================================\n                 QUI VA IL CONTENUTO DELL\'ARTICOLO'
    content_end = '<!-- Fine contenuto -->'
    
    if content_start in html and content_end in html:
        before = html.split(content_start)[0]
        after = html.split(content_end)[1]
        html = before + body_html + '\n\n            ' + content_end + after
    else:
        # Fallback: cerca un altro punto di inserimento
        html = re.sub(
            r'<div class="article-content">.*?(<div class="article-tags">)',
            f'<div class="article-content">\n            {body_html}\n\n            \\1',
            html,
            flags=re.DOTALL
        )
    
    # Gestisci immagine mancante
    if not image:
        # Rimuovi la sezione featured-image se non c'è immagine
        html = re.sub(
            r'<figure class="featured-image">.*?</figure>',
            '',
            html,
            flags=re.DOTALL
        )
    
    # Rimuovi sezione articoli correlati (per ora)
    html = re.sub(
        r'<section class="related-articles">.*?</section>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Pulisci placeholder rimanenti
    html = re.sub(r'\{\{[^}]+\}\}', '', html)
    
    return html

def update_blog_index(articles):
    """Aggiorna blog.html con la lista degli articoli."""
    blog_file = "blog.html"
    
    if not os.path.exists(blog_file):
        print("  ⚠️  blog.html non trovato")
        return
    
    with open(blog_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Genera le card degli articoli
    cards_html = ""
    for article in sorted(articles, key=lambda x: x['date'], reverse=True):
        image_html = f'<img src="{article["image"]}" alt="{article["image_alt"]}" class="blog-card-image">' if article['image'] else '<div class="blog-card-image"></div>'
        
        cards_html += f'''
        <a href="blog/{article['slug']}.html" class="blog-card">
            {image_html}
            <div class="blog-card-content">
                <span class="blog-card-category">{article['category']}</span>
                <h2>{article['title']}</h2>
                <p>{article['description'][:150]}...</p>
                <div class="blog-card-meta">
                    <span>📅 {article['date_formatted']}</span>
                    <span class="read-more">Leggi →</span>
                </div>
            </div>
        </a>
'''
    
    # Se non ci sono articoli, mostra stato vuoto
    if not cards_html:
        cards_html = '''
        <div class="empty-state">
            <h3>🌱 Prossimamente</h3>
            <p>Il blog è in arrivo. Iscriviti per ricevere notifiche sui nuovi articoli.</p>
            <a href="contatti.html" style="display: inline-block; margin-top: 1.5rem; padding: 0.8rem 1.5rem; background: linear-gradient(135deg, #8B4513, #A0522D); color: white; text-decoration: none; border-radius: 25px; font-size: 0.85rem;">Contattami</a>
        </div>
'''
    
    # Sostituisci il contenuto della griglia
    html = re.sub(
        r'(<div class="blog-grid">).*?(</div>\s*<div class="button-container">)',
        f'\\1{cards_html}\n    \\2',
        html,
        flags=re.DOTALL
    )
    
    with open(blog_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  ✅ blog.html aggiornato con {len(articles)} articoli")

def main():
    print("🔨 Build Blog - Casa Obàtálá")
    print("=" * 40)
    
    # Verifica esistenza cartelle
    if not os.path.exists(BLOG_FOLDER):
        print(f"❌ Cartella {BLOG_FOLDER}/ non trovata")
        return
    
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Template {TEMPLATE_FILE} non trovato")
        return
    
    # Leggi template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Trova tutti i file .md
    md_files = list(Path(BLOG_FOLDER).glob("*.md"))
    print(f"📄 Trovati {len(md_files)} file markdown")
    
    articles = []
    
    for md_file in md_files:
        print(f"  📝 Processo: {md_file.name}")
        
        html = build_article(str(md_file), template)
        
        if html:
            # Salva HTML
            output_file = md_file.with_suffix('.html')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  ✅ Creato: {output_file.name}")
            
            # Raccogli info per index
            with open(md_file, 'r', encoding='utf-8') as f:
                metadata, _ = parse_frontmatter(f.read())
            
            date = metadata.get('date', datetime.now())
            if isinstance(date, datetime):
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = str(date)
                
            articles.append({
                'slug': md_file.stem,
                'title': metadata.get('title', 'Senza titolo'),
                'description': metadata.get('description', ''),
                'date': date_str,
                'date_formatted': format_date_italian(date_str),
                'category': CATEGORIE.get(metadata.get('category', ''), 'Riflessioni'),
                'image': metadata.get('image', ''),
                'image_alt': metadata.get('image_alt', ''),
            })
    
    # Aggiorna blog.html
    print("\n📋 Aggiorno indice blog...")
    update_blog_index(articles)
    
    print("\n✨ Build completata!")

if __name__ == "__main__":
    main()
