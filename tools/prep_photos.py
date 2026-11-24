#!/usr/bin/env python3
"""Prepare build photos for the site.

Resizes each photo to at most 1600 px on the long side, applies the camera
rotation, and saves a new JPEG without any metadata (no GPS, no camera serial,
no date). Prints the <img> line with width and height for the log entry.

Usage:
    python3 tools/prep_photos.py OUT_DIR PHOTO [PHOTO ...]
    python3 tools/prep_photos.py site/photos/2026-12-06 ~/Desktop/IMG_1234.HEIC

Needs Pillow (pip install pillow); HEIC also needs pillow-heif.
Check every photo yourself before publishing: no photo that shows her.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener  # optional, for iPhone photos
    register_heif_opener()
except ImportError:
    pass

LONG_SIDE = 1600


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    site_root = next((p for p in out_dir.resolve().parents if p.name == "site"), None)
    for src in map(Path, sys.argv[2:]):
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
            dst = out_dir / (src.stem.lower().replace(" ", "-") + ".jpg")
            # A fresh image with no info dict: nothing from the original file is carried over.
            clean = Image.new("RGB", im.size)
            clean.paste(im)
            clean.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        with Image.open(dst) as chk:
            if chk.getexif() or chk.info.get("exif") or chk.info.get("xmp"):
                print(f"ERROR: metadata left in {dst}", file=sys.stderr)
                return 2
            w, h = chk.size
        rel = dst.resolve().relative_to(site_root) if site_root else dst
        print(f'<img src="{rel}" width="{w}" height="{h}" alt="" loading="lazy">')
    return 0


if __name__ == "__main__":
    sys.exit(main())
