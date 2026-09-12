from __future__ import annotations

"""Independent, read-only validator for AREA_01~20 INPUT V2 ZIPs."""

import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "RootDesk" / "MyDesk" / "GameData"
BASE = ROOT / "docs" / "art" / "images-input-packages"
OUT = ROOT / "docs" / "art" / "images-input-packages-v2"
AREA00_OUT = ROOT / "docs" / "art" / "area00-images-output" / "AREA_00_IMAGES_OUTPUT"
TARGETS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return digest(path.read_bytes())


def rows_file(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def rows_text(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def split(value: str) -> list[str]:
    return [x for x in (value or "").split("|") if x]


def walk_ruid(node) -> str:
    if isinstance(node, dict):
        if node.get("Name") == "SpriteRUID" and isinstance(node.get("Value"), str) and node["Value"]:
            return node["Value"]
        for value in node.values():
            found = walk_ruid(value)
            if found:
                return found
    if isinstance(node, list):
        for value in node:
            found = walk_ruid(value)
            if found:
                return found
    return ""


def skill_kind(row: dict[str, str]) -> str:
    if row.get("skill_kind") == "passive": return "패시브"
    if row.get("skill_kind") == "defense" or row.get("effect_type") == "shield": return "버프"
    return "액티브"


def main() -> None:
    baseline = json.loads((OUT / "SOURCE_BASELINE.json").read_text(encoding="utf-8"))
    areas = {r["id"]: r for r in rows_file(DATA / "AreaTable.csv")}
    rooms = rows_file(DATA / "RoomTable.csv")
    monsters = {r["id"]: r for r in rows_file(DATA / "MonsterTable.csv")}
    skill_blob = subprocess.check_output(["git", "show", "HEAD:RootDesk/MyDesk/GameData/SkillTable.csv"], cwd=ROOT)
    skills = {r["id"]: r for r in rows_text(skill_blob)}

    model_ruids = {}
    for path in (ROOT / "RootDesk" / "MyDesk" / "Models" / "Monsters").rglob("*.model"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        model_id = str(obj.get("EntryKey", "")).removeprefix("model://")
        if model_id and model_id not in model_ruids:
            model_ruids[model_id] = walk_ruid(obj)

    capture = defaultdict(list)
    for room in rooms:
        for mid in split(room.get("monster_id", "")):
            mon = monsters.get(mid)
            if mon and mon.get("drop_skill_id") and mid not in capture[room.get("area_id", "")]:
                capture[room.get("area_id", "")].append(mid)

    checks = []
    style_hashes = set()
    total_monsters = 0
    all_errors = []
    for aid in TARGETS:
        errors = []
        path = OUT / f"{aid.upper()}_IMAGES_INPUT_V2.zip"
        if not path.exists():
            errors.append("ZIP 없음")
            checks.append({"area_id": aid, "errors": errors})
            continue
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad: errors.append("CRC 오류: " + bad)
            root = f"{aid.upper()}_IMAGES_INPUT_V2/"
            names = set(z.namelist())
            required = [
                "PACKAGE_REVISION.md", "SOURCE_BASELINE.json", "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md",
                "AREA_MANIFEST.md", "AREA_MANIFEST.csv", "OUTPUT_FORMAT_SPEC.md", "OUTPUT_NAMING_SPEC.md",
                "MONSTER_IMAGE_PROVENANCE.csv", "global_skill_style_library/STYLE_INDEX.md",
                "global_skill_style_library/STYLE_INDEX.csv", "global_skill_style_library/summary/STYLE_ATLAS.md",
            ]
            for rel in required:
                if root + rel not in names: errors.append("필수 파일 누락: " + rel)
            if root + "AREA_MANIFEST.csv" not in names:
                manifest = []
            else:
                manifest = rows_text(z.read(root + "AREA_MANIFEST.csv"))
            total_monsters += len(manifest)
            mids = [r["monster_id"] for r in manifest]
            if set(mids) != set(capture.get(aid, [])):
                errors.append(f"실제 포획 배치와 manifest 불일치: actual={capture.get(aid, [])}, input={mids}")
            if len(mids) != len(set(mids)): errors.append("monster_id 중복")

            provenance = rows_text(z.read(root + "MONSTER_IMAGE_PROVENANCE.csv")) if root + "MONSTER_IMAGE_PROVENANCE.csv" in names else []
            prov_by_mid = {r["monster_id"]: r for r in provenance}
            for row in manifest:
                mid, sid = row["monster_id"], row["skill_id"]
                mon = monsters.get(mid)
                if not mon:
                    errors.append(f"MonsterTable 누락: {mid}")
                    continue
                if mon["drop_skill_id"] != sid: errors.append(f"drop_skill_id 불일치: {mid}")
                if mon["name"] != row["monster_name"]: errors.append(f"몬스터명 불일치: {mid}")
                if mon["level"] != row["level"]: errors.append(f"레벨 불일치: {mid}")
                skill = skills.get(sid)
                if skill:
                    if skill["name"] != row["skill_name"]: errors.append(f"스킬명 불일치: {sid}")
                    if skill_kind(skill) != row["skill_type"]: errors.append(f"스킬 타입 불일치: {sid}")
                elif sid != "s_mon_snail_dew_trail":
                    errors.append(f"HEAD SkillTable에도 없는 스킬: {sid}")
                folder = root + row["folder"].rstrip("/") + "/"
                for rel in ("MONSTER_IMAGE.png", "MONSTER_INFO.md", "SOURCE_PROVENANCE.md", "GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md"):
                    if folder + rel not in names: errors.append(f"{mid} 파일 누락: {rel}")
                image_name = folder + "MONSTER_IMAGE.png"
                if image_name in names:
                    data = z.read(image_name)
                    with Image.open(io.BytesIO(data)) as im:
                        rgba = im.convert("RGBA")
                        lo, hi = rgba.getchannel("A").getextrema()
                        if im.format != "PNG" or hi == 0 or rgba.getchannel("A").getbbox() is None:
                            errors.append(f"{mid} PNG/alpha 실패")
                    prov = prov_by_mid.get(mid)
                    if not prov: errors.append(f"{mid} provenance 행 없음")
                    else:
                        if prov["sha256"] != digest(data): errors.append(f"{mid} provenance SHA 불일치")
                        expected_ruid = model_ruids.get(mon["model_id"], "")
                        if prov["model_sprite_ruid"] != expected_ruid or row["monster_image_ruid"] != expected_ruid:
                            errors.append(f"{mid} model/RUID/image 연결 불일치")

            style_name = root + "global_skill_style_library/STYLE_INDEX.csv"
            styles = rows_text(z.read(style_name)) if style_name in names else []
            if len(styles) != 183: errors.append(f"style RUID 수 {len(styles)} != 183")
            elif {r.get("role_classification", "") for r in styles} - {"VFX", "ICON", "MONSTER_CHARACTER", "SCENE", "UNCONFIRMED"}:
                errors.append("알 수 없는 style role")
            if style_name in names: style_hashes.add(digest(z.read(style_name)))

            text_files = [n for n in names if n.endswith((".md", ".txt", ".csv", ".json"))]
            docs = "\n".join(z.read(n).decode("utf-8-sig", errors="replace") for n in text_files)
            banned = [
                ("사실상의 최신 우선", "RECENT_SECONDARY 자동 승격 잔존"),
                (f"{aid.upper()}_IMAGES_INPUT_IMAGES_OUTPUT", "구형 OUTPUT 루트 잔존"),
            ]
            for needle, msg in banned:
                if needle in docs: errors.append(msg)
            if re.search(r"(?<![A-Za-z0-9])[A-Za-z]:[/\\]", docs): errors.append("ZIP 외부 절대경로 의존")
            for needle, msg in [
                ("현재 `RECENT_SECONDARY`는 6차/HEXA 검색 후보", "시기 불확실성"),
                ("SHEET_SPLIT_MANIFEST.csv", "원본/분할 보존"),
                ("AUTO_VALIDATION", "자동검사/사용자승인 분리"),
                (f"출력 루트는 반드시 `{aid.upper()}_IMAGES_OUTPUT/`", "OUTPUT 루트"),
            ]:
                if needle not in docs: errors.append(msg + " 규칙 누락")

            # Approved reuse must be byte-identical to Area00 source.
            for mid in ("m_snail", "m_blue_snail", "m_slime"):
                if mid not in mids: continue
                candidates = [p for p in (AREA00_OUT / "monsters").iterdir() if f"_{mid}_" in p.name]
                if len(candidates) != 1:
                    errors.append(f"{mid} AREA00 source 탐색 실패")
                    continue
                source = candidates[0]
                prefix = root + "approved_reuse/AREA_00/" + source.name + "/"
                for file in source.rglob("*.png"):
                    name = prefix + file.relative_to(source).as_posix()
                    if name not in names: errors.append(f"{mid} 승인 재사용 누락: {file.name}")
                    elif digest(z.read(name)) != file_digest(file): errors.append(f"{mid} 승인 재사용 SHA 불일치: {file.name}")

        checks.append({"area_id": aid, "zip": path.relative_to(ROOT).as_posix(), "sha256": file_digest(path), "errors": errors, "status": "PASS" if not errors else "FAIL"})
        all_errors.extend(f"{aid}: {e}" for e in errors)

    if len(style_hashes) != 1: all_errors.append(f"공통 STYLE_INDEX 해시 불일치: {len(style_hashes)}종")
    if (OUT / "AREA_06_IMAGES_INPUT_V2.zip").exists(): all_errors.append("예약 area_06 ZIP이 생성됨")
    if set(TARGETS) - set(areas): all_errors.append("AreaTable 대상 Area 누락")

    frozen = baseline["area00_frozen_sha256"]
    area00_now = {
        "input_zip": file_digest(BASE / "AREA_00_IMAGES_INPUT.zip"),
        "output_manifest": file_digest(AREA00_OUT / "OUTPUT_MANIFEST.md"),
        "resource_map": file_digest(ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv"),
        "import_report": file_digest(ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_IMPORT_REPORT.md"),
    }
    if area00_now != frozen: all_errors.append("AREA 00 frozen hash changed")
    for key, rel in (("AreaTable", "AreaTable.csv"), ("RoomTable", "RoomTable.csv"), ("MonsterTable", "MonsterTable.csv"), ("GameBalance", "GameBalance.csv")):
        if file_digest(DATA / rel) != baseline[key]["sha256"]: all_errors.append(f"게임 데이터 변경: {rel}")

    summary = {
        "target_areas": len(TARGETS), "validated_zips": len(checks), "monster_placements": total_monsters,
        "pass": sum(x.get("status") == "PASS" for x in checks), "fail": sum(x.get("status") == "FAIL" for x in checks),
        "area06_absent": not (OUT / "AREA_06_IMAGES_INPUT_V2.zip").exists(),
        "common_style_hash_count": len(style_hashes), "area00_frozen": area00_now == frozen,
        "errors": all_errors,
    }
    (OUT / "INPUT_V2_INDEPENDENT_VALIDATION.json").write_text(json.dumps({"summary": summary, "areas": checks}, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    lines = ["# INPUT V2 VALIDATION — Independent Re-open", "", f"- 대상/ZIP: {summary['target_areas']}/{summary['validated_zips']}", f"- 몬스터 배치: {total_monsters}", f"- PASS/FAIL: {summary['pass']}/{summary['fail']}", f"- area_06 미생성: {summary['area06_absent']}", f"- 공통 STYLE_INDEX 해시 종류: {summary['common_style_hash_count']}", f"- AREA 00 frozen: {summary['area00_frozen']}", f"- 전체 오류: {'없음' if not all_errors else '; '.join(all_errors)}", "", "| Area | 결과 | ZIP SHA-256 | 오류 |", "|---|---|---|---|"]
    for row in checks:
        lines.append(f"| {row['area_id']} | {row.get('status','FAIL')} | `{row.get('sha256','')}` | {'; '.join(row['errors']) or '없음'} |")
    lines += ["", "검사 범위: ZIP CRC, 실제 RoomTable 포획 배치, MonsterTable/HEAD SkillTable 고정 필드, model SpriteRUID, MONSTER_IMAGE PNG·실제 alpha·provenance SHA, 필수 문서, 183개 공통 라이브러리 동일본, 구형 지시/절대경로 부재, AREA 00 승인 파일 바이트 재사용, AREA 00·게임 데이터 frozen hash.", "", "주의: 이미지 내용의 몬스터 적합성은 별도 contact sheet 시각 검수이며 이 픽셀/구조 검사가 사용자 아트 승인을 대신하지 않는다."]
    (OUT / "INPUT_V2_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if all_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
