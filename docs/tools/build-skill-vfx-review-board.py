"""Compose existing approved-review PNGs for visual inspection; never alter originals."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART_ROOTS = [
    ROOT / "docs/art/design-review-00-05/20260914_astra_review",
    ROOT / "docs/art/design-review-07-20/20260914_astra_review",
]
REPORT = ROOT / "docs/reports/skill-diversity-lore-rework-20260924"
with (REPORT / "LORE_DESIGN_66.csv").open(encoding="utf-8-sig", newline="") as handle:
    skills = list(csv.DictReader(handle))
if len(skills) != 66:
    raise RuntimeError(f"Expected 66 skills, got {len(skills)}")

tile_w, tile_h, cols, rows_per_page = 300, 230, 6, 6
font = ImageFont.load_default()
missing = []
for page_start in range(0, len(skills), cols * rows_per_page):
    page = Image.new("RGB", (tile_w * cols, tile_h * rows_per_page), (30, 32, 38))
    draw = ImageDraw.Draw(page)
    for local_index, row in enumerate(skills[page_start:page_start + cols * rows_per_page]):
        index = page_start + local_index
        x, y = (local_index % cols) * tile_w, (local_index // cols) * tile_h
        draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline=(84, 87, 96), width=2)
        draw.text((x + 8, y + 7), f"{index + 1:02d} {row['SkillID']}", font=font, fill=(240, 244, 252))
        draw.text((x + 8, y + 23), row['AfterBehavior'], font=font, fill=(185, 201, 224))
        dirs = [path for art_root in ART_ROOTS for path in art_root.glob(f"AREA_*/{row['SkillID']}")]
        if len(dirs) > 1 and any(path.parent.name == "AREA_00" for path in dirs):
            dirs = [path for path in dirs if path.parent.name == "AREA_00"]
        if len(dirs) != 1:
            missing.append((row['SkillID'], "directory", len(dirs)))
            continue
        files = list(dirs[0].glob("*.png"))
        icon = next((p for p in files if "_ICON" in p.name), None)
        frames = sorted(p for p in files if "_F" in p.name and "_ICON" not in p.name)
        frame = next((p for p in frames if "_F04" in p.name), None)
        if frame is None and frames:
            frame = frames[len(frames) // 2]
        for path, box in ((icon, (x + 8, y + 47, 82, 165)), (frame, (x + 97, y + 42, 195, 174))):
            if path is None:
                missing.append((row['SkillID'], "image", 0))
                continue
            with Image.open(path) as source:
                image = source.convert("RGBA")
                image.thumbnail((box[2], box[3]), Image.Resampling.LANCZOS)
                paste_x = box[0] + (box[2] - image.width) // 2
                paste_y = box[1] + (box[3] - image.height) // 2
                page.paste(image, (paste_x, paste_y), image)
        draw.text((x + 8, y + 211), f"Area {dirs[0].parent.name}", font=font, fill=(147, 159, 174))
    output = REPORT / f"VFX_REVIEW_BOARD_{page_start // (cols * rows_per_page) + 1:02d}.png"
    page.save(output)
    print(output)
print(f"reviewed={len(skills)} missing={missing}")
