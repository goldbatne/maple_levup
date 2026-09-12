#!/usr/bin/env python3
"""Apply a completed human/visual review sheet to one OUTPUT audit run.

This does not alter INPUT/OUTPUT archives or artwork.  It only updates the
run-local reports after every delivered monster/skill pair has been reviewed.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import audit_monster_skill_output as audit


REVIEW_FIELDS = [
    "area_id", "monster_id", "skill_id", "visual_status", "observation",
    "action", "review_basis",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("review_csv", type=Path)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    data_path = run_dir / "AUTO_AUDIT_DATA.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    reviews = read_csv(args.review_csv)
    review_map = {
        (r["area_id"], r["monster_id"], r["skill_id"]): r for r in reviews
    }
    pairs = {
        (i["area_id"], i["monster_id"], i["skill_id"])
        for i in data["items"] if i["monster_id"] and i["skill_id"]
    }
    missing = sorted(pairs - review_map.keys())
    invalid = sorted(
        (key, row["visual_status"])
        for key, row in review_map.items()
        if row["visual_status"] not in audit.VISUAL_STATUS
    )
    if missing or invalid:
        print(json.dumps({"missing_pairs": missing, "invalid_status": invalid}, ensure_ascii=False, indent=2))
        return 2

    for item in data["items"]:
        key = (item["area_id"], item["monster_id"], item["skill_id"])
        if key in review_map:
            item["visual_status"] = review_map[key]["visual_status"]

    for finding in data["findings"]:
        key = (finding["area_id"], finding["monster_id"], finding["skill_id"])
        review = review_map.get(key)
        if not review:
            continue
        finding["visual_status"] = review["visual_status"]
        if finding["action"] == "USER_REVIEW" and review["visual_status"] == "NO_OBVIOUS_ISSUE":
            finding["action"] = "NONE"
            finding["basis"] += "; resolved by actual contact-sheet/frame review"
        elif review["visual_status"] == "ISSUE_FOUND" and review["action"]:
            finding["action"] = review["action"]

    for area in data["areas"]:
        statuses = {
            review_map[p]["visual_status"] for p in pairs
            if p[0] == area["area_id"]
        }
        if "ISSUE_FOUND" in statuses:
            area["visual_status"] = "ISSUE_FOUND"
        elif "NEEDS_USER_REVIEW" in statuses:
            area["visual_status"] = "NEEDS_USER_REVIEW"
        elif statuses and statuses == {"NO_OBVIOUS_ISSUE"}:
            area["visual_status"] = "NO_OBVIOUS_ISSUE"
        else:
            area["visual_status"] = "NOT_CHECKED"

    target_review = run_dir / "VISUAL_REVIEW.csv"
    audit.write_csv(target_review, reviews, REVIEW_FIELDS)
    audit.write_reports(
        run_dir, data["areas"], data["items"], data["findings"], data["run"]
    )
    data_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    latest = audit.AUDIT_DIR / "LATEST_REPORT.md"
    visual_counts = Counter(a["visual_status"] for a in data["areas"])
    latest.write_text(
        "# Latest completed output audit\n\n"
        f"- run_id: `{data['run']['run_id']}`\n"
        f"- report: `{(run_dir / 'AUDIT_SUMMARY.md').resolve()}`\n"
        f"- rules_sha256: `{data['run']['rules_sha256']}`\n"
        f"- baseline_index_sha256: `{data['run']['baseline_index_sha256']}`\n"
        f"- visual review status: `COMPLETED` ({dict(visual_counts)})\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "run_id": data["run"]["run_id"],
        "reviewed_pairs": len(pairs),
        "visual_status": dict(visual_counts),
        "report": str((run_dir / "AUDIT_SUMMARY.md").resolve()),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
