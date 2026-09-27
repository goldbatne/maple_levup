"""Compose Maker screenshots for review; this does not alter source art."""
from pathlib import Path
import csv
import os
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / os.environ.get("VFX_REPORT_DIR", "docs/reports/skill-vfx-alignment-20260926")
DESIGN = ROOT / "docs/reports/skill-diversity-final-20260925/SKILL_66_FINAL_DESIGN.csv"
START = int(sys.argv[1]) if len(sys.argv) > 1 else 0
END = int(sys.argv[2]) if len(sys.argv) > 2 else START + 5
SHOT = int(sys.argv[3]) if len(sys.argv) > 3 else 1
PREFERRED = {
    ("s_mon_red_snail", "player"): 5,
    ("s_mon_fire_boar", "player"): 4,
    ("s_mon_blood_harp", "player"): 4,
    ("s_mon_lunar_pixie", "player"): 5,
    ("s_mon_slime", "monster"): 3,
    ("s_mon_chimera", "monster"): 4,
    ("s_mon_dodo", "player"): 2,
    ("s_mon_stumpy", "player"): 2,
    ("s_mon_jr_wraith", "player"): 2,
    ("s_mon_roid", "player"): 2,
    ("s_mon_star_pixie", "player"): 2,
    ("s_mon_shark", "player"): 2,
}
rows = list(csv.DictReader(DESIGN.open(encoding="utf-8-sig", newline="")))[START:END]
cell_w, cell_h = 415, 320
board = Image.new("RGB", (cell_w * 2, cell_h * len(rows)), "#18211f")
draw = ImageDraw.Draw(board)
font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)
for index, row in enumerate(rows):
    skill_id = row["SkillID"]
    for column, side in enumerate(("player", "monster")):
        folder = REPORT / "evidence" / side
        selected = PREFERRED.get((skill_id, side), SHOT) if SHOT == 1 else SHOT
        candidate = folder / f"{skill_id}_{selected}.png"
        if skill_id == "s_mon_memory_monk_trainee" and side == "player" and SHOT == 1:
            candidate = REPORT / "evidence/before-after/monk_after.png"
        if skill_id == "s_mon_official_knight_c" and side == "player" and SHOT == 1:
            candidate = REPORT / "evidence/before-after/knight_after.png"
        if not candidate.exists():
            candidate = folder / f"{skill_id}_1.png"
        x, y = column * cell_w, index * cell_h
        if candidate.exists():
            image = Image.open(candidate).convert("RGB")
            mid_x, mid_y = image.width // 2, image.height // 2
            crop = image.crop((mid_x - 200, mid_y - 140, mid_x + 200, mid_y + 160))
            board.paste(crop, (x + 7, y + 19))
        draw.text((x + 7, y + 2), f"{START+index+1:02d} {skill_id} / {side}",
                  fill="white", font=font)
suffix = "" if SHOT == 1 else f"_SHOT{SHOT}"
out = REPORT / f"VFX_BOARD_{START+1:02d}_{END:02d}{suffix}.png"
board.save(out)
print(out)
