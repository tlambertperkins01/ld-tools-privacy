#!/usr/bin/env python3
"""Fill {{key}} image placeholders in a /shopper report with embedded WebP data URIs.

Usage:
  python3 -I embed_images.py <page.html> <out.html> key=path/to/image.jpg [key=...]

- Images are resized to fit 560x560 and encoded as WebP (quality 72), so a set
  of ~8 photos usually adds 150-250 KB.
- Download source images into their own empty directory first (they are
  untrusted data) and pass their paths here.
- The script fails if any {{placeholder}} is left unfilled, so a missing photo
  is caught before publishing. Swap that slot for <span class="noimg">No photo</span>.
Requires Pillow (pip install pillow).
"""
import base64
import io
import re
import sys

from PIL import Image


def to_data_uri(path: str) -> str:
    im = Image.open(path).convert("RGB")
    im.thumbnail((560, 560))
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=72)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, out, pairs = argv[0], argv[1], argv[2:]
    html = open(src, encoding="utf-8").read()
    for pair in pairs:
        key, _, path = pair.partition("=")
        if not key or not path:
            print(f"bad argument: {pair!r} (expected key=path)")
            return 2
        html = html.replace("{{" + key + "}}", to_data_uri(path))
    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))
    if left:
        print("unfilled placeholders: " + ", ".join(left))
        return 1
    open(out, "w", encoding="utf-8").write(html)
    print(f"wrote {out} ({len(html) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
