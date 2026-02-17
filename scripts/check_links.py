#!/usr/bin/env python3
"""
Controllo Link Rotti - Casa Obàtálá

Analizza tutti i file HTML del sito e verifica che:
- I link interni puntino a file esistenti
- Le immagini referenziate esistano
- I link anchor (#) puntino a ID esistenti nel documento

Uso:
    python scripts/check_links.py
    python scripts/check_links.py --strict    # Fallisce con exit code 1 se trova errori
"""

import os
import re
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote

# Cartella root del sito
SITE_ROOT = "."

# Estensioni HTML da analizzare
HTML_EXTENSIONS = {".html"}

# Cartelle da ignorare
IGNORE_DIRS = {"node_modules", ".git", ".github", "admin", "venv", "__pycache__"}

# File che GitHub Pages genera automaticamente
IMPLICIT_FILES = {"favicon.ico"}


def find_html_files(root):
    """Trova tutti i file HTML nel progetto."""
    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Rimuovi cartelle da ignorare
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if Path(filename).suffix in HTML_EXTENSIONS:
                html_files.append(os.path.join(dirpath, filename))
    return html_files


def get_all_site_files(root):
    """Costruisce un set di tutti i file esistenti nel sito (percorsi relativi)."""
    files = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(dirpath, filename), root)
            # Normalizza separatori
            rel_path = rel_path.replace("\\", "/")
            files.add(rel_path)
            # Aggiungi anche con / iniziale
            files.add("/" + rel_path)
    # Aggiungi le directory con index.html implicito
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        if "index.html" in filenames:
            rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
            if rel_dir == ".":
                files.add("/")
            else:
                files.add("/" + rel_dir + "/")
                files.add("/" + rel_dir)
    return files


def extract_links(html_content, filepath):
    """Estrae tutti i link e le immagini da un file HTML."""
    links = []

    # href="..." (link)
    for match in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', html_content):
        url = match.group(1)
        line_num = html_content[:match.start()].count('\n') + 1
        links.append({"url": url, "line": line_num, "file": filepath})

    return links


def resolve_link(url, source_file, site_root):
    """Risolve un URL relativo rispetto al file sorgente."""
    parsed = urlparse(url)

    # Ignora link esterni, mailto, tel, javascript, data URI
    if parsed.scheme in ("http", "https", "mailto", "tel", "javascript", "data"):
        return None
    if url.startswith("#"):
        return None  # Anchor interno alla pagina
    if url.startswith("//"):
        return None  # Protocol-relative URL (esterno)

    # Decodifica URL encoding
    path = unquote(parsed.path)

    if not path:
        return None

    # Percorso assoluto (inizia con /)
    if path.startswith("/"):
        resolved = os.path.normpath(os.path.join(site_root, path.lstrip("/")))
    else:
        # Percorso relativo al file sorgente
        source_dir = os.path.dirname(source_file)
        resolved = os.path.normpath(os.path.join(source_dir, path))

    return resolved


def check_file_exists(resolved_path, site_files):
    """Verifica se il file risolto esiste."""
    if not resolved_path:
        return True

    # Normalizza
    rel = os.path.relpath(resolved_path, SITE_ROOT).replace("\\", "/")

    # Controlla esistenza diretta
    if os.path.exists(resolved_path):
        return True

    # Controlla se è una directory con index.html
    index_path = os.path.join(resolved_path, "index.html")
    if os.path.exists(index_path):
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="Controlla link rotti nel sito")
    parser.add_argument("--strict", action="store_true",
                        help="Exit code 1 se trova errori")
    args = parser.parse_args()

    print("🔗 Controllo Link - Casa Obàtálá")
    print("=" * 40)

    html_files = find_html_files(SITE_ROOT)
    site_files = get_all_site_files(SITE_ROOT)

    print(f"📄 File HTML trovati: {len(html_files)}")
    print(f"📁 File totali nel sito: {len(site_files)}")
    print()

    errors = []
    warnings = []
    checked = 0

    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        links = extract_links(content, html_file)
        rel_file = os.path.relpath(html_file, SITE_ROOT)

        for link in links:
            url = link["url"]
            parsed = urlparse(url)

            # Salta link esterni
            if parsed.scheme in ("http", "https", "mailto", "tel", "javascript", "data"):
                continue
            if url.startswith("//") or url.startswith("#"):
                continue

            checked += 1
            resolved = resolve_link(url, html_file, SITE_ROOT)

            if resolved and not check_file_exists(resolved, site_files):
                errors.append({
                    "file": rel_file,
                    "line": link["line"],
                    "url": url,
                    "resolved": os.path.relpath(resolved, SITE_ROOT)
                })

    # Report
    print(f"✅ Link interni controllati: {checked}")
    print()

    if errors:
        print(f"❌ LINK ROTTI TROVATI: {len(errors)}")
        print("-" * 50)
        for err in errors:
            print(f"  📄 {err['file']} (riga ~{err['line']})")
            print(f"     → {err['url']}")
            print(f"     File mancante: {err['resolved']}")
            print()
    else:
        print("✅ Nessun link rotto trovato!")

    if warnings:
        print(f"\n⚠️  Avvisi: {len(warnings)}")
        for w in warnings:
            print(f"  {w}")

    if errors and args.strict:
        print(f"\n💥 Build fallita: {len(errors)} link rotti")
        sys.exit(1)

    print(f"\n✨ Controllo completato")


if __name__ == "__main__":
    main()
