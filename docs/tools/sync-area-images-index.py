import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "images-input-packages"
csv_path = OUT / "ALL_AREAS_INDEX.csv"
md_path = OUT / "ALL_AREAS_INDEX.md"

with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
columns = list(rows[0])
for row in rows:
    row["zip_bytes"] = str((ROOT / row["zip_path"]).stat().st_size)
with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=columns)
    w.writeheader()
    w.writerows(rows)

text = md_path.read_text(encoding="utf-8")
for row in rows:
    pattern = re.compile(rf"(?m)^\| {re.escape(row['area_order'])} \| {re.escape(row['area_id'])} \|.*$")
    replacement = "| " + " | ".join(row[c] for c in columns) + " |"
    text = pattern.sub(lambda _: replacement, text)
md_path.write_text(text, encoding="utf-8")
print(sum(int(row["zip_bytes"]) for row in rows))
