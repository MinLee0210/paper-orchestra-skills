#!/usr/bin/env python3
"""Render PDF pages to PNGs, optionally as 2x2 review grids."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_pages(spec: str | None, total: int) -> list[int]:
    if not spec:
        return list(range(total))
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start) - 1, int(end)))
        else:
            pages.append(int(part) - 1)
    return [p for p in pages if 0 <= p < total]


def make_grids(image_paths: list[Path], outdir: Path) -> list[Path]:
    try:
        from PIL import Image
    except ImportError:
        print("warning: Pillow not installed; skipping 2x2 grids", file=sys.stderr)
        return []

    grids: list[Path] = []
    for start in range(0, len(image_paths), 4):
        chunk = [Image.open(path).convert("RGB") for path in image_paths[start : start + 4]]
        width = max(image.width for image in chunk)
        height = max(image.height for image in chunk)
        canvas = Image.new("RGB", (width * 2, height * 2), "white")
        for index, image in enumerate(chunk):
            x = (index % 2) * width
            y = (index // 2) * height
            canvas.paste(image, (x, y))
        grid_path = outdir / f"grid_{start // 4 + 1}.png"
        canvas.save(grid_path)
        grids.append(grid_path)
        for image in chunk:
            image.close()
    return grids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf")
    parser.add_argument("outdir")
    parser.add_argument("--dpi", type=int, default=120)
    parser.add_argument("--pages", help="1-based selection, e.g. 1-4,7")
    parser.add_argument("--grid", action="store_true", help="Also write 2x2 grids")
    args = parser.parse_args()

    try:
        import pymupdf  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            print("error: PyMuPDF is required: pip install pymupdf", file=sys.stderr)
            return 2

    pdf = Path(args.pdf).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    if not pdf.exists():
        print(f"error: {pdf} does not exist", file=sys.stderr)
        return 2
    outdir.mkdir(parents=True, exist_ok=True)

    zoom = args.dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)
    written: list[Path] = []

    with pymupdf.open(pdf) as doc:
        selected = parse_pages(args.pages, doc.page_count)
        for index in selected:
            page = doc[index]
            pix = page.get_pixmap(matrix=matrix)
            path = outdir / f"page_{index + 1:03d}.png"
            pix.save(path)
            written.append(path)

    print(f"Rendered {len(written)} pages to {outdir}")
    if args.grid:
        grids = make_grids(written, outdir)
        print(f"Wrote {len(grids)} grids")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
