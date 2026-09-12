from __future__ import annotations

import csv
import io
import re
import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages"
WORK = OUT / "_alpha_fix"


def remove_edge_background(path: Path) -> tuple[int, int]:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
    before = rgba.getchannel("A").getextrema()
    if before == (255, 255):
        corners = [(0, 0), (rgba.width - 1, 0), (0, rgba.height - 1), (rgba.width - 1, rgba.height - 1)]
        colors = [rgba.getpixel(p) for p in corners]
        base = colors[0]
        if all(max(abs(c[i] - base[i]) for i in range(3)) <= 12 for c in colors):
            for point, color in zip(corners, colors):
                ImageDraw.floodfill(rgba, point, (color[0], color[1], color[2], 0), thresh=18)
    rgba.save(path, "PNG", optimize=True)
    return rgba.getchannel("A").getextrema()


if WORK.exists():
    shutil.rmtree(WORK)
WORK.mkdir(parents=True)

changed = 0
for zip_path in sorted(OUT.glob("AREA_*_IMAGES_INPUT.zip")):
    stage = WORK / zip_path.stem
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(stage)
    for image_path in stage.rglob("MONSTER_IMAGE.png"):
        lo, hi = remove_edge_background(image_path)
        if lo < 255:
            changed += 1
        folder = image_path.parent
        for numbered in folder.glob("[0-9][0-9][0-9]_*.png"):
            shutil.copy2(image_path, numbered)
        info = folder / "MONSTER_INFO.md"
        if info.exists():
            text = info.read_text(encoding="utf-8")
            text = re.sub(r"- alpha range: .*", f"- alpha range: {lo}~{hi}", text)
            info.write_text(text, encoding="utf-8")
    temp_zip = zip_path.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(stage).as_posix())
    temp_zip.replace(zip_path)
    shutil.rmtree(stage)

shutil.rmtree(WORK)
print(f"transparent monster references: {changed}")
