"""Side-by-side Maker captures only; no original PNG or generated art is edited."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/reports/skill-vfx-meaning-20260926"
PAIRS = [
    ("s_mon_mushroom", "player", 1, 1),
    ("s_mon_fairy", "player", 1, 1),
    ("s_mon_octopus", "player", 1, 1),
    ("s_mon_drumming_bunny", "player", 1, 2),
    ("s_mon_king_clang", "monster", 1, 1),
    ("s_mon_cygnus", "player", 1, 1),
    ("s_mon_mutant_stumpy", "monster", 1, 1),
]
DEST = REPORT / "evidence/comparison"
DEST.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 16)
for skill_id, side, before_shot, after_shot in PAIRS:
    before_path = REPORT / f"evidence/{side}/{skill_id}_{before_shot}.png"
    after_group = "after_fast" if skill_id == "s_mon_mutant_stumpy" else "after_final"
    after_path = REPORT / f"{after_group}/evidence/{side}/{skill_id}_{after_shot}.png"
    if not before_path.exists() or not after_path.exists():
        continue
    before = Image.open(before_path).convert("RGB")
    after = Image.open(after_path).convert("RGB")
    if before.size != after.size:
        raise ValueError(f"Mismatched Maker screenshot sizes: {skill_id}")
    width, height = before.size
    board = Image.new("RGB", (width * 2, height + 38), "#202324")
    board.paste(before, (0, 38))
    board.paste(after, (width, 38))
    draw = ImageDraw.Draw(board)
    draw.text((12, 8), f"BEFORE  {skill_id} / {side}", font=font, fill="white")
    draw.text((width + 12, 8), f"AFTER  {skill_id} / {side}", font=font, fill="white")
    out = DEST / f"{skill_id}_{side}.png"
    board.save(out)
    print(out)

ADJUSTED = [
    "s_mon_mushroom", "s_mon_dark_axe_stump", "s_mon_fairy", "s_mon_octopus",
    "s_mon_tauromacis", "s_mon_eliza", "s_mon_squid", "s_mon_drumming_bunny",
    "s_mon_chronos", "s_mon_timer", "s_mon_meercat", "s_mon_homun", "s_mon_deo",
    "s_mon_king_clang", "s_mon_zeno", "s_mon_advanced_knight_b", "s_mon_cygnus",
    "s_mon_ancient_dark_golem", "s_mon_mutant_stumpy",
]
tile_w, tile_h = 422, 270
overview = Image.new("RGB", (tile_w * 2, tile_h * len(ADJUSTED)), "#202324")
draw = ImageDraw.Draw(overview)
for row, skill_id in enumerate(ADJUSTED):
    for col, side in enumerate(("player", "monster")):
        group = "after_fast" if (skill_id == "s_mon_mutant_stumpy" and side == "monster") or (
            skill_id == "s_mon_squid" and side == "player") else "after_final"
        folder = REPORT / f"{group}/evidence/{side}"
        shot = folder / f"{skill_id}_1.png"
        if skill_id == "s_mon_drumming_bunny" and side == "player":
            shot = folder / f"{skill_id}_2.png"
        if skill_id == "s_mon_squid" and side == "player":
            shot = folder / f"{skill_id}_2.png"
        if not shot.exists():
            continue
        picture = Image.open(shot).convert("RGB")
        picture.thumbnail((tile_w, tile_h - 30))
        overview.paste(picture, (col * tile_w, row * tile_h + 30))
        draw.text((col * tile_w + 6, row * tile_h + 5),
                  f"{skill_id} / {side}", font=font, fill="white")
out = REPORT / "ADJUSTED_19_AFTER_OVERVIEW.png"
overview.save(out)
print(out)
