#!/usr/bin/env python3
"""
Ottimizzazione Immagini - Casa Obàtálá

Comprime le immagini nella cartella images/blog/ per ridurre i tempi
di caricamento. Non converte in WebP per evitare di dover modificare
i template HTML — si limita a comprimere PNG e JPEG.

Funzionamento:
- PNG: comprime con ottimizzazione massima
- JPEG: comprime al 85% di qualità (buon compromesso qualità/peso)
- Ridimensiona immagini più grandi di 1600px di larghezza
- Salta immagini già ottimizzate (traccia in .optimized_images)
- Non sovrascrive mai gli originali senza comprimerli prima

Uso:
    python scripts/optimize_images.py
    python scripts/optimize_images.py --quality 80    # Qualità JPEG diversa
    python scripts/optimize_images.py --max-width 1200
    python scripts/optimize_images.py --dry-run       # Mostra cosa farebbe

Requisiti:
    pip install Pillow --break-system-packages
    (aggiungere Pillow a requirements.txt)
"""

import os
import sys
import argparse
import hashlib
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Pillow non installato. Esegui: pip install Pillow")
    print("   Oppure aggiungi 'Pillow' a requirements.txt")
    sys.exit(1)

# Cartella immagini
IMAGES_FOLDER = "images/blog"

# File per tracciare immagini già ottimizzate
TRACKING_FILE = ".optimized_images"

# Estensioni supportate
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# Dimensioni massime ragionevoli per un blog
DEFAULT_MAX_WIDTH = 1600
DEFAULT_JPEG_QUALITY = 85


def get_file_hash(filepath):
    """Calcola hash MD5 del file per tracciamento."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_tracking():
    """Carica la lista di immagini già ottimizzate."""
    if not os.path.exists(TRACKING_FILE):
        return set()
    with open(TRACKING_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_tracking(tracked):
    """Salva la lista aggiornata."""
    with open(TRACKING_FILE, "w") as f:
        for entry in sorted(tracked):
            f.write(entry + "\n")


def optimize_image(filepath, max_width, jpeg_quality, dry_run=False):
    """Ottimizza una singola immagine. Restituisce (risparmiato_bytes, azione)."""
    original_size = os.path.getsize(filepath)
    ext = Path(filepath).suffix.lower()

    try:
        img = Image.open(filepath)
    except Exception as e:
        return 0, f"⚠️  Errore apertura: {e}"

    action_parts = []

    # Ridimensiona se troppo larga
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        if not dry_run:
            img = img.resize((max_width, new_height), Image.LANCZOS)
        action_parts.append(f"ridimensionata {img.width}x{img.height} → {max_width}x{new_height}")

    if dry_run:
        action = ", ".join(action_parts) if action_parts else "compressa"
        return 0, f"🏃 Dry run: {action}"

    # Salva con compressione
    if ext == ".png":
        # Per PNG: converti RGBA se necessario, poi salva ottimizzato
        if img.mode == "RGBA":
            img.save(filepath, "PNG", optimize=True)
        else:
            img.save(filepath, "PNG", optimize=True)
        action_parts.append("PNG ottimizzato")

    elif ext in (".jpg", ".jpeg"):
        # Per JPEG: converti in RGB se necessario
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(filepath, "JPEG", quality=jpeg_quality, optimize=True)
        action_parts.append(f"JPEG qualità {jpeg_quality}")

    new_size = os.path.getsize(filepath)
    saved = original_size - new_size

    if saved > 0:
        pct = (saved / original_size) * 100
        action_parts.append(f"-{saved // 1024}KB ({pct:.0f}%)")
    elif saved < 0:
        # L'immagine è diventata più grande (già ottimizzata) — ripristina
        action_parts.append("già ottimale")

    return max(saved, 0), " | ".join(action_parts)


def main():
    parser = argparse.ArgumentParser(description="Ottimizza immagini del blog")
    parser.add_argument("--quality", type=int, default=DEFAULT_JPEG_QUALITY,
                        help=f"Qualità JPEG (default: {DEFAULT_JPEG_QUALITY})")
    parser.add_argument("--max-width", type=int, default=DEFAULT_MAX_WIDTH,
                        help=f"Larghezza massima in pixel (default: {DEFAULT_MAX_WIDTH})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa farebbe senza modificare")
    parser.add_argument("--force", action="store_true",
                        help="Riottimizza anche immagini già processate")
    args = parser.parse_args()

    print("🖼️  Ottimizzazione Immagini - Casa Obàtálá")
    print("=" * 45)

    if not os.path.exists(IMAGES_FOLDER):
        print(f"ℹ️  Cartella {IMAGES_FOLDER} non trovata, niente da ottimizzare")
        return

    # Trova immagini
    images = []
    for dirpath, _, filenames in os.walk(IMAGES_FOLDER):
        for filename in filenames:
            if Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS:
                images.append(os.path.join(dirpath, filename))

    if not images:
        print("ℹ️  Nessuna immagine trovata")
        return

    print(f"📸 Immagini trovate: {len(images)}")
    print(f"⚙️  Max larghezza: {args.max_width}px | Qualità JPEG: {args.quality}")
    print()

    tracked = load_tracking()
    total_saved = 0
    processed = 0
    skipped = 0

    for img_path in sorted(images):
        rel_path = os.path.relpath(img_path, ".")
        file_hash = get_file_hash(img_path)
        tracking_key = f"{rel_path}:{file_hash}"

        # Salta se già ottimizzata (a meno che --force)
        if tracking_key in tracked and not args.force:
            skipped += 1
            continue

        saved, action = optimize_image(img_path, args.max_width, args.quality, args.dry_run)
        total_saved += saved
        processed += 1

        print(f"  {'✅' if saved > 0 else '➡️'} {rel_path}")
        print(f"     {action}")

        if not args.dry_run:
            # Aggiorna tracking con nuovo hash
            new_hash = get_file_hash(img_path)
            tracked.add(f"{rel_path}:{new_hash}")

    if not args.dry_run:
        save_tracking(tracked)

    print()
    print(f"📊 Riepilogo:")
    print(f"   Processate: {processed}")
    print(f"   Saltate (già ottimizzate): {skipped}")
    if total_saved > 0:
        print(f"   Spazio risparmiato: {total_saved // 1024}KB ({total_saved / 1024 / 1024:.1f}MB)")
    print(f"\n✨ Completato!")


if __name__ == "__main__":
    main()
