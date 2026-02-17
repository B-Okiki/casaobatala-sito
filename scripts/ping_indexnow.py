#!/usr/bin/env python3
"""
IndexNow - Ping automatico a Bing dopo ogni build
Casa Obàtálá

Questo script:
1. Legge la sitemap.xml per ottenere tutti gli URL pubblicati
2. Invia un ping IndexNow a Bing con gli URL modificati
3. Può inviare tutti gli URL o solo quelli modificati di recente

Uso:
    python scripts/ping_indexnow.py                    # Invia tutti gli URL
    python scripts/ping_indexnow.py --changed-only     # Solo URL con lastmod recente
    python scripts/ping_indexnow.py --urls URL1 URL2   # URL specifici

Requisiti:
    - Variabile d'ambiente INDEXNOW_KEY con la chiave API
    - File {INDEXNOW_KEY}.txt nella root del sito
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SITE_URL = "https://casaobatala.it"
SITEMAP_FILE = "sitemap.xml"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"


def get_api_key():
    """Recupera la chiave API da variabile d'ambiente."""
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    if not key:
        print("❌ Variabile d'ambiente INDEXNOW_KEY non impostata")
        print("   Genera una chiave su: https://www.bing.com/indexnow")
        print("   Poi aggiungila come secret in GitHub: Settings > Secrets > INDEXNOW_KEY")
        sys.exit(1)
    return key


def parse_sitemap(sitemap_path, changed_only=False, days=3):
    """Estrae gli URL dalla sitemap.xml.
    
    Se changed_only=True, restituisce solo gli URL con lastmod
    negli ultimi `days` giorni.
    """
    if not os.path.exists(sitemap_path):
        print(f"❌ Sitemap non trovata: {sitemap_path}")
        sys.exit(1)

    with open(sitemap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Estrai coppie (loc, lastmod)
    urls = []
    blocks = re.findall(r"<url>(.*?)</url>", content, re.DOTALL)

    cutoff = datetime.now() - timedelta(days=days)

    for block in blocks:
        loc_match = re.search(r"<loc>(.*?)</loc>", block)
        lastmod_match = re.search(r"<lastmod>(.*?)</lastmod>", block)

        if not loc_match:
            continue

        url = loc_match.group(1).strip()

        if changed_only and lastmod_match:
            try:
                lastmod = datetime.strptime(lastmod_match.group(1).strip(), "%Y-%m-%d")
                if lastmod < cutoff:
                    continue
            except ValueError:
                pass  # Se non riesce a parsare, include l'URL

        urls.append(url)

    return urls


def ping_indexnow(urls, api_key):
    """Invia un batch di URL a IndexNow.
    
    IndexNow supporta fino a 10.000 URL per richiesta.
    La notifica viene condivisa automaticamente con tutti i motori
    di ricerca partecipanti (Bing, Yandex, Seznam.cz, Naver).
    """
    if not urls:
        print("ℹ️  Nessun URL da inviare")
        return True

    # IndexNow accetta max 10.000 URL per batch
    batch_size = 10000
    success = True

    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]

        payload = {
            "host": "casaobatala.it",
            "key": api_key,
            "keyLocation": f"{SITE_URL}/{api_key}.txt",
            "urlList": batch
        }

        data = json.dumps(payload).encode("utf-8")

        req = Request(
            INDEXNOW_ENDPOINT,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )

        try:
            response = urlopen(req, timeout=30)
            status = response.getcode()

            if status == 200:
                print(f"✅ IndexNow: {len(batch)} URL inviati con successo (HTTP {status})")
            elif status == 202:
                print(f"✅ IndexNow: {len(batch)} URL accettati per elaborazione (HTTP {status})")
            else:
                print(f"⚠️  IndexNow: risposta HTTP {status}")

        except HTTPError as e:
            status = e.code
            if status == 422:
                print(f"⚠️  IndexNow: URL non validi o chiave errata (HTTP 422)")
                print(f"   Verifica che il file {api_key}.txt sia accessibile su {SITE_URL}/{api_key}.txt")
            elif status == 429:
                print(f"⚠️  IndexNow: troppi invii, riprova più tardi (HTTP 429)")
            else:
                print(f"❌ IndexNow: errore HTTP {status} - {e.reason}")
            success = False

        except URLError as e:
            print(f"❌ IndexNow: errore di rete - {e.reason}")
            success = False

    return success


def main():
    parser = argparse.ArgumentParser(description="Ping IndexNow con gli URL del sito")
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Invia solo gli URL modificati negli ultimi 3 giorni"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Numero di giorni per --changed-only (default: 3)"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="URL specifici da inviare (ignora la sitemap)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra gli URL senza inviarli"
    )

    args = parser.parse_args()

    print("🔔 IndexNow - Casa Obàtálá")
    print("=" * 40)

    api_key = get_api_key()
    print(f"🔑 Chiave API: {api_key[:8]}...")

    # Determina gli URL da inviare
    if args.urls:
        urls = args.urls
        print(f"📋 URL specificati manualmente: {len(urls)}")
    else:
        urls = parse_sitemap(SITEMAP_FILE, changed_only=args.changed_only, days=args.days)
        mode = f"modificati ultimi {args.days} giorni" if args.changed_only else "tutti"
        print(f"📋 URL dalla sitemap ({mode}): {len(urls)}")

    if not urls:
        print("ℹ️  Nessun URL da inviare")
        return

    # Mostra gli URL
    for url in urls:
        print(f"   → {url}")

    if args.dry_run:
        print(f"\n🏃 Dry run: {len(urls)} URL NON inviati")
        return

    # Invia
    print(f"\n📡 Invio a IndexNow...")
    success = ping_indexnow(urls, api_key)

    if success:
        print(f"\n✨ Completato! Bing e gli altri motori partecipanti sono stati notificati.")
    else:
        print(f"\n⚠️  Completato con errori. Controlla i messaggi sopra.")
        sys.exit(1)


if __name__ == "__main__":
    main()
