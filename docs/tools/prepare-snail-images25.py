"""Prepare the adopted Images 2.5 snail skill sheet without re-layout or re-centering."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw


SOURCE = Path(r"C:/Users/dddd/AppData/Local/Temp/codex-clipboard-3684d7de-b135-454e-8881-18056f6b56bd.png")
OUTPUT = Path(r"D:/maplestory_levup/docs/art/pilot-snail-images25/output")
ORIGINAL = OUTPUT / "OUT_SNAIL_DEW_TRAIL_SHEET_ORIGINAL.png"
NORMALIZED = OUTPUT / "OUT_SNAIL_DEW_TRAIL_SHEET_1024x512.png"
FRAMES = OUTPUT / "frames"
PIVOT_OVERLAY = OUTPUT / "PIVOT_CHECK_64_128.png"
MANIFEST = OUTPUT / "FRAME_MANIFEST.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def edge_alpha_counts(alpha: Image.Image) -> dict[str, dict[str, int]]:
    width, height = alpha.size
    pixels = alpha.load()
    edges = {
        "left": [pixels[0, y] for y in range(height)],
        "right": [pixels[width - 1, y] for y in range(height)],
        "top": [pixels[x, 0] for x in range(width)],
        "bottom": [pixels[x, height - 1] for x in range(width)],
    }
    return {
        name: {
            "nonzero": sum(1 for value in values if value > 0),
            "above_16": sum(1 for value in values if value > 16),
            "above_64": sum(1 for value in values if value > 64),
            "max": max(values),
        }
        for name, values in edges.items()
    }


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)

    source_hash = sha256(SOURCE)
    if ORIGINAL.exists() and sha256(ORIGINAL) != source_hash:
        raise RuntimeError(f"Original preservation target already differs: {ORIGINAL}")
    if not ORIGINAL.exists():
        shutil.copy2(SOURCE, ORIGINAL)

    with Image.open(SOURCE) as opened:
        rgba = opened.convert("RGBA")
        source_meta = {
            "path": str(SOURCE),
            "preserved_path": str(ORIGINAL),
            "sha256": source_hash,
            "size": list(rgba.size),
            "mode": rgba.mode,
            "alpha_extrema": list(rgba.getchannel("A").getextrema()),
            "corner_rgba": list(rgba.getpixel((0, 0))),
        }
        normalized = rgba.resize((1024, 512), Image.Resampling.LANCZOS)

    normalized.save(NORMALIZED, format="PNG")

    overlay = normalized.copy()
    draw = ImageDraw.Draw(overlay)
    frame_rows: list[dict[str, object]] = []
    for index in range(8):
        col = index % 4
        row = index // 4
        box = (col * 256, row * 256, (col + 1) * 256, (row + 1) * 256)
        frame = normalized.crop(box)
        frame_path = FRAMES / f"snail_dew_trail_f{index:02d}.png"
        frame.save(frame_path, format="PNG")

        alpha = frame.getchannel("A")
        bbox = alpha.getbbox()
        alpha_values = list(alpha.getdata())
        nonzero = sum(1 for value in alpha_values if value > 0)
        fully_opaque = sum(1 for value in alpha_values if value == 255)
        edge_counts = edge_alpha_counts(alpha)
        pivot = (64, 128)
        frame_rows.append(
            {
                "index": index,
                "path": str(frame_path),
                "sha256": sha256(frame_path),
                "size": list(frame.size),
                "mode": frame.mode,
                "alpha_extrema": list(alpha.getextrema()),
                "alpha_bbox": list(bbox) if bbox else None,
                "nonzero_alpha_pixels": nonzero,
                "fully_opaque_pixels": fully_opaque,
                "edge_alpha_pixels": edge_counts,
                "edge_crossing_any_alpha": any(
                    stats["nonzero"] > 0 for stats in edge_counts.values()
                ),
                "edge_crossing_visible_alpha": any(
                    stats["above_16"] > 0 for stats in edge_counts.values()
                ),
                "pivot_pixel": list(pivot),
                "pivot_normalized": [0.25, 0.5],
                "pivot_alpha": alpha.getpixel(pivot),
            }
        )

        center_x = col * 256 + pivot[0]
        center_y = row * 256 + pivot[1]
        draw.line((center_x - 8, center_y, center_x + 8, center_y), fill=(255, 0, 255, 255), width=1)
        draw.line((center_x, center_y - 8, center_x, center_y + 8), fill=(255, 0, 255, 255), width=1)

    overlay.save(PIVOT_OVERLAY, format="PNG")
    manifest = {
        "source": source_meta,
        "normalization": {
            "method": "whole-sheet resize only; no crop, trim, per-frame translation, or recentering",
            "resampling": "Pillow Image.Resampling.LANCZOS",
            "normalized_path": str(NORMALIZED),
            "normalized_sha256": sha256(NORMALIZED),
            "normalized_size": [1024, 512],
            "grid": [4, 2],
            "frame_size": [256, 256],
            "read_order": "left-to-right, top-to-bottom",
            "pivot_pixel": [64, 128],
            "pivot_normalized": [0.25, 0.5],
            "pivot_overlay_path": str(PIVOT_OVERLAY),
        },
        "frames": frame_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    blocking = [
        row["index"]
        for row in frame_rows
        if row["alpha_bbox"] is None or row["edge_crossing_visible_alpha"]
    ]
    print(json.dumps({"manifest": str(MANIFEST), "blocking_frames": blocking, "frames": frame_rows}, ensure_ascii=False, indent=2))
    return 2 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
