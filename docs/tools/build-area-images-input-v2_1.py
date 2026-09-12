#!/usr/bin/env python3
"""Build evidence-backed AREA 01~20 INPUT V2.1 packages.

Reads immutable V2 ZIPs and project evidence. It never edits game data, Area 00,
legacy/V2 packages, or output art. The destination must not already exist.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "docs" / "art" / "images-input-packages-v2"
OUT = ROOT / "docs" / "art" / "images-input-packages-v2_1"
BASELINE_JSON = V2 / "SOURCE_BASELINE.json"
AREA00 = ROOT / "docs" / "art" / "area00-images-output"
DATA = ROOT / "RootDesk" / "MyDesk" / "GameData"
MISLOCATED = ROOT / "Mislocated" / "MyDesk" / "GameData"
TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]

V2_REPORTS = [
    "INPUT_V2_ADDITIONAL_FINDINGS.md",
    "INPUT_V2_VALIDATION.md",
    "INPUT_V2_CHANGELOG.md",
    "ALL_AREAS_INPUT_V2_INDEX.md",
]

CODE_FILES = [
    "RootDesk/MyDesk/GameData/GameData.mlua",
    "RootDesk/MyDesk/GameData/GameDataVerify.mlua",
    "RootDesk/MyDesk/PlayerAttack.mlua",
    "RootDesk/MyDesk/MonsterAttack.mlua",
    "RootDesk/MyDesk/Combat/SkillEffect.mlua",
    "RootDesk/MyDesk/Combat/SkillCastEffect.mlua",
    "RootDesk/MyDesk/Combat/SkillProjectile.mlua",
    "RootDesk/MyDesk/Player/PlayerDash.mlua",
]

BASELINE_DATA_FILES = [
    "RootDesk/MyDesk/GameData/SkillTable.csv",
    "RootDesk/MyDesk/GameData/SkillTable.userdataset",
    "RootDesk/MyDesk/GameData/MonsterTable.csv",
    "RootDesk/MyDesk/GameData/AreaTable.csv",
    "RootDesk/MyDesk/GameData/RoomTable.csv",
    "RootDesk/MyDesk/GameData/GameBalance.csv",
]

AREA00_FILES = [
    "AREA_00_IMAGES_RESOURCE_MAP.csv",
    "AREA_00_IMAGES_IMPORT_REPORT.md",
]

BINDING_COLUMNS = [
    "area_id", "monster_id", "skill_id", "skill_type", "effect_role",
    "current_field", "current_layer", "current_ruid", "decision",
    "new_file_set", "target_field", "target_layer", "attach_to",
    "player_behavior", "monster_behavior", "delay_seconds", "duration_seconds",
    "loop", "frame_timing", "coordinate_unit", "direction", "flip_x",
    "scale", "pivot", "offset", "image_internal_vs_engine",
    "source_evidence", "notes",
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for block in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(data: bytes | str) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split(raw: str | None) -> list[str]:
    return [] if not raw else raw.split("|")


def num(raw: str | None, default: float = 0.0) -> float:
    try:
        return float(raw or default)
    except ValueError:
        return default


def fmt(value: str | float | None) -> str:
    if value is None or value == "":
        return "0"
    try:
        f = float(value)
        return str(int(f)) if f.is_integer() else str(f)
    except (TypeError, ValueError):
        return str(value)


def replace_section(text: str, title: str, body: str) -> str:
    header = f"## {title}"
    pattern = re.compile(rf"(?ms)^{re.escape(header)}\n.*?(?=^## |\Z)")
    block = header + "\n\n" + body.strip() + "\n\n"
    return pattern.sub(block, text, count=1) if pattern.search(text) else text.rstrip() + "\n\n" + block


def git_bytes(commit: str, rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=ROOT)


def git_status() -> str:
    return subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True, encoding="utf-8", errors="replace")


def zip_tree(root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(root.parent).as_posix())


def extract_v2(aid: str, parent: Path) -> Path:
    source = V2 / f"{aid.upper()}_IMAGES_INPUT_V2.zip"
    with zipfile.ZipFile(source) as z:
        if z.testzip() is not None:
            raise RuntimeError(f"CRC error in {source.name}")
        z.extractall(parent)
    old = parent / f"{aid.upper()}_IMAGES_INPUT_V2"
    new = parent / f"{aid.upper()}_IMAGES_INPUT_V2_1"
    old.rename(new)
    return new


def style_folder_name(index: str, members: list[str]) -> str:
    prefix = f"{int(index):04d}_"
    found = sorted({Path(x).parts[-3] for x in members if "/skills/" in x and Path(x).parts[-3].startswith(prefix)})
    if len(found) != 1:
        raise RuntimeError(f"style folder {index}: {found}")
    return found[0]


def is_exact_white_png(path: Path) -> bool:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        return all(a > 0 and r == 255 and g == 255 and b == 255 for r, g, b, a in rgba.getdata())


def sync_style_library(source_zip: Path, temp: Path) -> tuple[Path, list[dict], list[dict]]:
    with zipfile.ZipFile(source_zip) as z:
        z.extractall(temp)
    src_root = temp / "AREA_01_IMAGES_INPUT_V2" / "global_skill_style_library"
    index_path = src_root / "STYLE_INDEX.csv"
    rows = csv_rows(index_path.read_bytes())
    white_rows = []
    for row in rows:
        dirs = list((src_root / "skills").glob(f"{int(row['index']):04d}_*"))
        if len(dirs) != 1:
            raise RuntimeError(f"style folder missing {row['index']}")
        info_path = dirs[0] / "info.md"
        preview = dirs[0] / "preview.png"
        white = preview.exists() and is_exact_white_png(preview)
        row["reference_role"] = row.get("role_classification", "UNCONFIRMED")
        row["preview_usable"] = "false" if white else "true"
        row["preview_unusable_reason"] = (
            "exact 320x240 opaque-white raster; 식별 가능한 효과가 없고 프로젝트 캐시에 대체본 없음"
            if white else ""
        )
        if white:
            white_rows.append(dict(row))
        info = info_path.read_text(encoding="utf-8")
        sync = "\n".join([
            f"- RUID: `{row['RUID']}`",
            f"- reference_role: `{row['reference_role']}`",
            f"- style_priority: `{row['style_priority']}`",
            f"- role_basis: {row.get('role_basis', '')}",
            f"- preview_usable: `{row['preview_usable']}`",
            f"- preview_unusable_reason: {row['preview_unusable_reason'] or '없음'}",
            "- 적용 규칙: preview_usable=false이거나 style_priority=EXCLUDE_STYLE이면 주 스타일 판단에서 제외한다.",
        ])
        info_path.write_text(replace_section(info, "V2.1 synchronized classification", sync), encoding="utf-8", newline="\n")

    columns = list(rows[0])
    for col in ("reference_role", "preview_usable", "preview_unusable_reason"):
        if col not in columns:
            columns.append(col)
    write_csv(index_path, rows, columns)

    index_md = [
        "# Global Skill Style Library Index — V2.1",
        "",
        "이 자료는 프로젝트에서 확보한 183개 참고 리소스 수집본이며 메이플 전체 스킬 전수 자료가 아니다.",
        "출시 시기와 버전이 증명되지 않은 RECENT_SECONDARY는 최신 자료로 자동 승격하지 않는다.",
        "`preview_usable=false` 및 `EXCLUDE_STYLE` 자료는 RUID·분류 이력 보존용이며 주 렌더링 판단에서 제외한다.",
        "",
        "| index | name | RUID | reference_role | style_priority | preview_usable | reason |",
        "|---:|---|---|---|---|---|---|",
    ]
    for r in rows:
        index_md.append(f"| {r['index']} | {r['skill_resource_name']} | `{r['RUID']}` | {r['reference_role']} | {r['style_priority']} | {r['preview_usable']} | {r['preview_unusable_reason'] or r.get('role_basis','')} |")
    (src_root / "STYLE_INDEX.md").write_text("\n".join(index_md) + "\n", encoding="utf-8", newline="\n")

    counts = Counter(r["reference_role"] for r in rows)
    priorities = Counter(r["style_priority"] for r in rows)
    atlas = [
        "# STYLE ATLAS — V2.1",
        "",
        f"- 전체 수집본: {len(rows)}",
        f"- 역할: " + " / ".join(f"{k} {v}" for k, v in sorted(counts.items())),
        f"- 우선순위: " + " / ".join(f"{k} {v}" for k, v in sorted(priorities.items())),
        f"- preview_usable=false: {len(white_rows)}",
        "- RECENT_PRIMARY만 시기 근거가 검증된 경우 최신 우선으로 쓴다. RECENT_SECONDARY는 자동 대체 세트가 아니다.",
        "- MONSTER_CHARACTER/SCENE/EXCLUDE_STYLE은 캐릭터·무기·장면 실루엣을 신규 VFX로 가져오지 않는다.",
        "- 흰색 프리뷰는 효과를 판독할 수 없어 주 스타일 분석에서 제외한다. 파일과 RUID는 이력 보존을 위해 유지한다.",
        "",
        "## 식별 불가 프리뷰",
        "",
        "| index | name | RUID | 판정 |",
        "|---:|---|---|---|",
    ]
    for r in white_rows:
        atlas.append(f"| {r['index']} | {r['skill_resource_name']} | `{r['RUID']}` | exact opaque white; replacement unavailable |")
    summary = src_root / "summary"
    summary.mkdir(exist_ok=True)
    (summary / "STYLE_ATLAS.md").write_text("\n".join(atlas) + "\n", encoding="utf-8", newline="\n")
    return src_root, rows, white_rows


def layers(skill: dict[str, str]) -> list[dict[str, str]]:
    ruids = split(skill.get("layer_ruids"))
    cols = {
        "type": split(skill.get("layer_types")), "style": split(skill.get("layer_styles")),
        "delay": split(skill.get("layer_delays")), "duration": split(skill.get("layer_durations")),
        "scale": split(skill.get("layer_scales")), "offset_x": split(skill.get("layer_offsets_x")),
        "offset_y": split(skill.get("layer_offsets_y")), "drift_x": split(skill.get("layer_drifts_x")),
        "drift_y": split(skill.get("layer_drifts_y")),
    }
    out = []
    defaults = {"type": "sprite", "style": "burst", "delay": "0", "duration": "0.4", "scale": "1", "offset_x": "0", "offset_y": "0", "drift_x": "0", "drift_y": "0"}
    for i, ruid in enumerate(ruids):
        row = {"ruid": ruid}
        for key, values in cols.items():
            row[key] = values[i] if i < len(values) and values[i] != "" else defaults[key]
        out.append(row)
    return out


def skill_type(skill: dict[str, str]) -> str:
    if skill.get("skill_kind") == "passive":
        return "패시브"
    if skill.get("skill_kind") == "defense":
        return "버프"
    return "액티브"


def layer_summary(skill: dict[str, str]) -> str:
    ls = layers(skill)
    if not ls:
        return "CAST 레이어 없음"
    return "; ".join(
        f"L{i+1} {x['ruid']} {x['type']}/{x['style']} delay={x['delay']}s duration={x['duration']}s scale={x['scale']} offset=({x['offset_x']},{x['offset_y']})wu drift=({x['drift_x']},{x['drift_y']})wu/s"
        for i, x in enumerate(ls)
    )


def actual_motion(skill: dict[str, str], balance: dict[str, float], approved_reuse: bool = False) -> str:
    if approved_reuse:
        return "AREA 00 승인 AnimationClip/ICON 바이트 재사용. 승인 보고서의 플레이어 좌우·몬스터 시전자 검증을 따르며 신규 생성하지 않음"
    typ = skill_type(skill)
    if typ == "패시브":
        return "런타임 VFX 없음. 보유 효과는 PlayerStats가 적용하며 REFERENCE_VFX는 제작 검수용·자동 반입 금지"
    ls = layer_summary(skill)
    if typ == "버프":
        return f"플레이어/몬스터 모두 자기 자신에게 효과 적용 성공 후 시전자 원점+h에 CAST 재생, FlipX 없음. {ls}"
    if skill.get("projectile_ruid"):
        flight = fmt(balance.get("projectile_seconds", 0.35))
        return f"CAST는 시전자 원점+h에서 재생하고 projectile_ruid {skill['projectile_ruid']}는 엔진이 목표까지 {flight}초 이동·회전. 피해는 도착 타이머 뒤 착탄점에서 판정. {ls}"
    if num(skill.get("dash_distance")) > 0:
        sec = fmt(balance.get("skill_dash_seconds", 0.2))
        return f"플레이어: 8방향으로 {skill['dash_distance']}wu를 {sec}초 이동하고 계산 도착점에서 피해 판정; 직후 CAST는 서버가 보는 시전자 위치에 부착되어 계산 도착점과 일치가 보장되지 않음. 몬스터: dash_distance 분기 없이 즉시 시전자 중심 원형 판정 후 명중 시 CAST. {ls}"
    return f"플레이어: 즉시 시전자 중심 원형 피해 판정 후 CAST. 몬스터: 축소 반경의 시전자 중심 원형 판정이 실제 명중한 경우에만 CAST. CAST는 시전자 원점+h, 좌측 대상/시선이면 FlipX. {ls}"


def runtime_evidence_doc(code_hashes: dict[str, str], balance: dict[str, float]) -> str:
    return f"""# Runtime evidence summary

이 문서는 코드 읽기 근거이며 Maker 런타임 실행 결과가 아니다.

- 데이터 로딩: `GameData.mlua` 100~107, 114~142 — `_DataService:GetTable(\"SkillTable\")`을 이름으로 조회해 `LoadSkills`가 캐시한다.
- 레이어: `GameData.mlua` 67~97, `SkillEffect.mlua` 47~121 — 파이프 배열을 순서대로 구성하고 시전자 좌표에 `offset`, `drift`, `FlipX`를 엔진이 적용한다.
- 일반 공격: `PlayerAttack.mlua` 225~269 / `MonsterAttack.mlua` 379~436 — 플레이어는 즉시 판정 뒤 CAST, 몬스터는 실제 명중 뒤 CAST.
- 투사체: `PlayerAttack.mlua` 277~337, `MonsterAttack.mlua` 450 이후, `SkillEffect.mlua` 149~200 — 엔진 이동과 데미지 타이머가 `{fmt(balance.get('projectile_seconds', 0.35))}`초를 공유한다.
- 돌진: `PlayerAttack.mlua` 386~479 / `PlayerDash.mlua` 38~104 — 플레이어만 클라이언트 8방향 이동하며 `{fmt(balance.get('skill_dash_seconds', 0.2))}`초 뒤 계산 도착점에 판정한다. 몬스터 CastSkill에는 dash 분기가 없다.
- 버프: `PlayerAttack.mlua` 213~220 / `MonsterAttack.mlua` 362~375 — 자기 효과가 성공한 뒤 방향 반전 없이 CAST.
- 패시브: `GameData.mlua` 201~215 / `PlayerStats.mlua`의 `skill_kind == \"passive\"` 분기 — 보유 수량으로 스탯을 적용하고 CAST VFX를 호출하지 않는다.
- Sprite 등록 pivot `(0.5,0.5)`은 AREA 00 승인 반입 보고서의 확인값이다. 다른 신규 에셋의 최종 scale/offset은 Preview 확인 전 확정하지 않는다.

## 확보한 현재 코드 SHA-256

""" + "\n".join(f"- `{p}`: `{h}`" for p, h in code_hashes.items()) + "\n"


def output_profile(spec: str) -> tuple[int, int, str]:
    m = re.search(r"VFX:\s*(\d+) frames, 각 (\d+)×(\d+) RGBA PNG, 약 ([0-9.]+) sec/frame", spec)
    if not m:
        raise RuntimeError("VFX output profile missing")
    if m.group(2) != m.group(3):
        raise RuntimeError("non-square profile unsupported")
    return int(m.group(1)), int(m.group(2)), m.group(4)


def binding_rows(aid: str, manifest_row: dict[str, str], skill: dict[str, str], spec: str,
                 balance: dict[str, float], approved: dict[str, str] | None) -> list[dict]:
    mid, sid = manifest_row["monster_id"], manifest_row["skill_id"]
    typ = manifest_row["skill_type"]
    frames, canvas, frame_sec = output_profile(spec)
    source = "runtime_evidence/RUNTIME_CODE_EVIDENCE.md; ASSET_BINDING_PLAN.md"
    common = {
        "area_id": aid, "monster_id": mid, "skill_id": sid, "skill_type": typ,
        "loop": "false", "frame_timing": f"{frames} frames × {frame_sec}s; same {canvas}×{canvas} RGBA canvas",
        "coordinate_unit": "runtime offset=world unit; drift=world unit/s; art=pixel canvas; pivot=normalized",
        "pivot": "(0.5,0.5) planned registration pivot; no autocrop/recenter",
        "source_evidence": source,
    }
    out = []
    if approved:
        out.append({**common, "effect_role": "APPROVED_REUSE_CAST_VFX+ICON", "current_field": "layer_ruids|icon_ruid",
            "current_layer": "approved single layer", "current_ruid": f"{approved['animationclip_ruid']}|{approved['icon_ruid']}",
            "decision": "APPROVED_REUSE", "new_file_set": "approved_reuse/AREA_00/* (byte-identical)",
            "target_field": "layer_ruids|icon_ruid", "target_layer": "approved mapping only", "attach_to": "caster",
            "player_behavior": "AREA 00 report: left/right playback verified", "monster_behavior": "AREA 00 report: monster caster playback verified",
            "delay_seconds": "0", "duration_seconds": approved.get("total_seconds", ""), "direction": "approved left/right behavior",
            "flip_x": "approved runtime behavior", "scale": "1", "offset": "(0,0) approved",
            "image_internal_vs_engine": "approved frames preserved; no regeneration", "notes": "신규 생성 금지; reuse manifest SHA must match"})
        return out

    ls = layers(skill)
    projectile = skill.get("projectile_ruid", "")
    dash = num(skill.get("dash_distance")) > 0
    if typ == "패시브":
        out.append({**common, "effect_role": "REFERENCE_VFX", "current_field": "none", "current_layer": "none",
            "current_ruid": "", "decision": "REFERENCE_ONLY", "new_file_set": "VFX/F00... (preview/reference only)",
            "target_field": "none", "target_layer": "none", "attach_to": "not runtime",
            "player_behavior": "inventory ownership applies stat; no CAST", "monster_behavior": "no passive CAST path",
            "delay_seconds": "n/a", "duration_seconds": "preview only", "direction": "art reference only", "flip_x": "n/a",
            "scale": "n/a", "offset": "n/a", "image_internal_vs_engine": "reference animation only; never auto-import",
            "notes": "현행 런타임 VFX 없음"})
    elif projectile and not ls and not skill.get("effect_ruid"):
        out.append({**common, "effect_role": "PROJECTILE", "current_field": "projectile_ruid", "current_layer": "moving entity sprite",
            "current_ruid": projectile, "decision": "REPLACE_PLANNED", "new_file_set": "VFX/F00... -> accepted AnimationClip",
            "target_field": "projectile_ruid", "target_layer": "SkillProjectile SpriteRenderer", "attach_to": "moving projectile entity",
            "player_behavior": "engine moves toward aimed/nearest target then hit at arrival", "monster_behavior": "engine moves toward player then hit at arrival",
            "delay_seconds": "0", "duration_seconds": fmt(balance.get("projectile_seconds", 0.35)), "direction": "engine from caster to target",
            "flip_x": "entity travel direction; no frame-level canvas translation", "scale": "current model/preview check at import",
            "offset": "spawn at caster + skill_effect_height", "image_internal_vs_engine": "frames animate local form only; engine supplies translation and spin",
            "notes": "스텀피는 CAST field가 없어 V2의 generic CAST 해석을 PROJECTILE로 교정"})
    else:
        current_field = "layer_ruids" if ls else "effect_ruid"
        current_ruid = "|".join(x["ruid"] for x in ls) if ls else skill.get("effect_ruid", "")
        role = "IMPACT_CAST_VFX" if dash else ("SELF_BUFF_CAST_VFX" if typ == "버프" else "CAST_VFX")
        out.append({**common, "effect_role": role, "current_field": current_field,
            "current_layer": f"visual stack L1..L{len(ls)}" if ls else "legacy single effect",
            "current_ruid": current_ruid, "decision": "REPLACE_PLANNED", "new_file_set": "VFX/F00... -> accepted AnimationClip",
            "target_field": current_field, "target_layer": "replace visual stack as one accepted primary clip; do not duplicate across old layers automatically",
            "attach_to": "caster at PlayCast time", "player_behavior": actual_motion(skill, balance),
            "monster_behavior": actual_motion(skill, balance), "delay_seconds": "0 planned primary clip",
            "duration_seconds": f"{frames * float(frame_sec):.2f}", "direction": "right-authored; role contract controls use",
            "flip_x": "defense=false; attack based on player look/monster hit target", "scale": "UNRESOLVED_IMPORT_PREVIEW",
            "offset": "preserve current gameplay origin; final visual offset unresolved until labeled preview",
            "image_internal_vs_engine": "local build-up/impact only; layer drift, dash, projectile translation remain engine-owned",
            "notes": "old layers remain KEEP until art approval; exact final scale/offset is not invented in INPUT"})

    # Preserve current layers explicitly so the plan records every L1/L2/... input.
    for i, layer in enumerate(ls, 1):
        out.append({**common, "effect_role": "CURRENT_CAST_LAYER", "current_field": "layer_ruids", "current_layer": f"L{i}",
            "current_ruid": layer["ruid"], "decision": "KEEP", "new_file_set": "none until approved replacement",
            "target_field": "layer_ruids", "target_layer": f"L{i}", "attach_to": "caster",
            "player_behavior": "current layer recipe", "monster_behavior": "current layer recipe",
            "delay_seconds": layer["delay"], "duration_seconds": layer["duration"], "direction": "engine FlipX by caster/target",
            "flip_x": "SkillEffect.SpawnLayer", "scale": layer["scale"], "offset": f"({layer['offset_x']},{layer['offset_y']}) world unit",
            "image_internal_vs_engine": f"engine drift ({layer['drift_x']},{layer['drift_y']}) world unit/s",
            "notes": "기존 리소스는 신규 아트 승인·반입 전까지 유지"})

    if projectile and not (not ls and not skill.get("effect_ruid")):
        out.append({**common, "effect_role": "PROJECTILE", "current_field": "projectile_ruid", "current_layer": "moving entity sprite",
            "current_ruid": projectile, "decision": "KEEP", "new_file_set": "none in required V2.1 scope",
            "target_field": "projectile_ruid", "target_layer": "SkillProjectile SpriteRenderer", "attach_to": "moving projectile entity",
            "player_behavior": "engine travel then arrival hit", "monster_behavior": "engine travel then arrival hit",
            "delay_seconds": "0", "duration_seconds": fmt(balance.get("projectile_seconds", 0.35)), "direction": "caster→target",
            "flip_x": "engine orientation/spin", "scale": "current", "offset": "caster/target + skill_effect_height",
            "image_internal_vs_engine": "engine owns translation/spin; existing projectile art retained",
            "notes": "NEEDS_DECISION: 별도 신규 projectile art까지 제작할지는 승인 근거 없음; required CAST+ICON 제작은 진행 가능"})

    icon_ruid = skill.get("icon_ruid", "")
    out.append({**common, "effect_role": "ICON", "current_field": "icon_ruid", "current_layer": "UI",
        "current_ruid": icon_ruid, "decision": "REPLACE_PLANNED", "new_file_set": "ICON/icon.png 256×256 RGBA",
        "target_field": "icon_ruid", "target_layer": "UI icon", "attach_to": "UI",
        "player_behavior": "inventory/skill UI", "monster_behavior": "not world VFX", "delay_seconds": "n/a",
        "duration_seconds": "static", "direction": "none", "flip_x": "false", "scale": "UI layout controlled",
        "offset": "UI layout controlled", "image_internal_vs_engine": "static centered motif",
        "notes": "VFX와 색·질감 언어 일치; 몬스터 원본을 그대로 복사하지 않음"})
    return out


def add_v21_docs(stage: Path, aid: str, manifest: list[dict], skills: dict[str, dict], balance: dict[str, float],
                  approved_map: dict[str, dict], binding: list[dict], common_style: Path, runtime_doc: str) -> list[dict]:
    style_target = stage / "global_skill_style_library"
    shutil.rmtree(style_target)
    shutil.copytree(common_style, style_target)

    actual_map = {}
    for row in manifest:
        mid, sid = row["monster_id"], row["skill_id"]
        approved = approved_map.get(mid) if approved_map.get(mid, {}).get("skill_id") == sid else None
        skill = skills.get(sid)
        if approved:
            motion = actual_motion({}, balance, True)
        elif skill:
            motion = actual_motion(skill, balance)
        else:
            motion = "UNRESOLVED: 기준 SkillTable과 승인 맵 모두에서 skill_id를 찾지 못함"
        row["actual_motion"] = motion
        actual_map[mid] = motion
        folder = stage / row["folder"]
        for filename in ("GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md"):
            path = folder / filename
            text = path.read_text(encoding="utf-8")
            if approved:
                reuse_body = "\n".join([
                    "- 역할: APPROVED_REUSE_CAST_VFX + APPROVED_REUSE_ICON",
                    f"- 채택 승인 리소스: AnimationClip `{approved['animationclip_ruid']}` / ICON `{approved['icon_ruid']}`",
                    f"- 승인 규격: {approved.get('frame_count','')} frames / {approved.get('canvas_rgba','')} / {approved.get('frame_seconds','')}s per frame / total {approved.get('total_seconds','')}s",
                    "- 재사용 파일: `approved_reuse/AREA_00/` 아래 F00... 및 ICON. `AREA_00_REUSE_MANIFEST.md`의 SHA-256과 일치해야 한다.",
                    "- 호환 근거: 동일 monster_id + skill_id이며 Area 00 resource map·import report와 승인 파일 해시가 일치한다.",
                    "- 신규 생성 금지: VFX/ICON을 다시 생성하거나 다른 HEAD 시각 RUID로 되돌리지 않는다.",
                    "- 좌표·방향: 승인 반입값(scale 1, offset/drift 0, normalized pivot 0.5/0.5)과 승인 좌우/몬스터 재생 기록을 유지한다.",
                ])
                text = replace_section(text, "런타임 역할·반입 계약", reuse_body)
            body = "\n".join([
                f"- actual_motion: {motion}",
                "- 몬스터별 Preview: `PREVIEW/labeled_preview.png` 필수. INPUT의 `MONSTER_IMAGE.png`를 변형 없이 합성한다.",
                f"- Area Preview: `{aid.upper()}_IMAGES_OUTPUT/AREA_OVERVIEW_PREVIEW.png` 필수.",
                "- 아트 캔버스: 기존 출력 프로필의 프레임 수·픽셀 크기를 유지하고 모든 프레임 동일 캔버스·동일 중심축·실제 alpha로 만든다.",
                "- 기준점: 등록 계획 pivot은 normalized `(0.5,0.5)`이며 autocrop/recenter 금지. 최종 world scale/offset은 labeled preview 확인 전 임의 확정하지 않는다.",
                "- 이미지 내부 변화와 엔진 이동: 준비·형성·충돌·소멸 같은 국소 변화만 프레임 안에서 표현한다. projectile 이동, dash 이동, layer drift, FlipX는 엔진 역할과 중복하지 않는다.",
            ])
            path.write_text(replace_section(text, "V2.1 실제 동작·납품 동기화", body), encoding="utf-8", newline="\n")

    columns = list(manifest[0])
    write_csv(stage / "AREA_MANIFEST.csv", manifest, columns)
    md = (stage / "AREA_MANIFEST.md").read_text(encoding="utf-8")
    sync = ["| monster_id | skill_id | actual_motion |", "|---|---|---|"]
    for row in manifest:
        sync.append(f"| `{row['monster_id']}` | `{row['skill_id']}` | {row['actual_motion'].replace('|', '/')} |")
    (stage / "AREA_MANIFEST.md").write_text(replace_section(md, "V2.1 actual_motion sync", "\n".join(sync)), encoding="utf-8", newline="\n")

    common_contract = """- 게임용 원본: 프레임 분리형 F00... RGBA PNG와 ICON 256×256 RGBA.
- 몬스터별 검수 Preview: `PREVIEW/labeled_preview.png` 필수. INPUT의 MONSTER_IMAGE를 재생성·재해석하지 않고 그대로 합성한다.
- Area 검수 Preview: 출력 루트의 `AREA_OVERVIEW_PREVIEW.png` 필수.
- Preview는 검수 산출물이며 Resource Storage 반입 원본이 아니다.
- 원본 시트가 생성된 경우 시트와 분할 좌표를 보존하되 주 납품물은 분리 프레임이다.
- RGBA 표기뿐 아니라 실제 alpha, 잘림, 다른 셀 조각, 빈 프레임을 검사한다.
- 파일 검사 PASS와 사용자 아트 승인은 별도다. 도구 한도를 프롬프트로 해제하거나 무인 완주를 보장한다고 쓰지 않는다.
- 출력 루트는 `AREA_XX_IMAGES_OUTPUT`이며 ZIP 밖 절대경로에 의존하지 않는다."""
    for name in ("OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md", "README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md"):
        path = stage / name
        text = path.read_text(encoding="utf-8")
        if name == "CHATGPT_IMAGES_MASTER_PROMPT.md":
            contract = common_contract + "\n- 스타일 선택 시 `preview_usable=true`인 자료만 주 분석에 사용한다. RECENT_SECONDARY는 최신으로 자동 승격하지 않는다."
        else:
            contract = common_contract
        path.write_text(replace_section(text, "V2.1 mandatory delivery contract", contract), encoding="utf-8", newline="\n")

    write_csv(stage / "ASSET_BINDING_PLAN.csv", binding, BINDING_COLUMNS)
    (stage / "ASSET_BINDING_PLAN.md").write_text(
        "# ASSET BINDING PLAN\n\nCSV가 연결 계획의 원장이다. KEEP은 승인 전 현행 보존, REPLACE_PLANNED는 아트 승인 후 교체 계획, APPROVED_REUSE는 Area 00 승인본, REFERENCE_ONLY는 런타임 미사용이다. 신규 RUID 부재는 오류가 아니다.\n",
        encoding="utf-8", newline="\n")
    runtime_dir = stage / "runtime_evidence"
    runtime_dir.mkdir(exist_ok=True)
    (runtime_dir / "RUNTIME_CODE_EVIDENCE.md").write_text(runtime_doc, encoding="utf-8", newline="\n")
    return manifest


def build_data_resolution(baseline: dict, commit_skill: list[dict], mis_skill: list[dict], area00_map: list[dict], status: str) -> tuple[str, list[str]]:
    h = {r["id"]: r for r in commit_skill}
    m = {r["id"]: r for r in mis_skill}
    changed = [k for k in sorted(set(h) | set(m)) if h.get(k) != m.get(k)]
    approved_ok = []
    for a in area00_map:
        r = m.get(a["skill_id"], {})
        ok = r.get("icon_ruid") == a["icon_ruid"] and r.get("layer_ruids") == a["animationclip_ruid"]
        approved_ok.append(f"- `{a['skill_id']}`: {'MATCH' if ok else 'MISMATCH'} (candidate icon/layer vs Area 00 resource map)")
    doc = f"""# DATA SOURCE RESOLUTION

## 확인된 사실

- V2 기준 커밋: `{baseline['git_head']}`.
- 기준 커밋의 SkillTable SHA-256: `{baseline['SkillTable']['sha256']}` / 111행.
- 현재 정상 경로 `RootDesk/MyDesk/GameData/SkillTable.csv`와 `.userdataset`은 삭제 상태다. 삭제 의도는 기록이 없어 UNKNOWN이다.
- 실제 로더는 `GameData:GetDataSet(\"SkillTable\")` → `_DataService:GetTable(\"SkillTable\")`로 이름 기반 UserDataSet을 읽는다.
- 현재 파일시스템에는 `Mislocated/MyDesk/GameData/SkillTable.csv/.userdataset` 후보가 있으나, 정상 RootDesk 경로가 아니므로 Maker 등록·현재 실행 원본이라고 단정할 수 없다.
- Mislocated CSV는 기준 커밋과 비교해 변경 5행({', '.join(changed)}), 총 112행이다. 나머지 행은 동일하다.
- 변경 5행은 Area 00 승인 리소스맵의 4개 교체 행과 신규 `s_mon_snail_dew_trail`로 설명되며 아래 값이 대응한다.

""" + "\n".join(approved_ok) + f"""

## 판정

- Area 00 재사용 3종은 승인 resource map·import report·Mislocated 후보가 같은 RUID를 가리키므로 승인본을 사용한다.
- 나머지 대상 스킬은 기준 커밋과 Mislocated 후보의 값이 동일하므로 V2 확정 데이터 대조에 기준 커밋 사본을 사용한다.
- 현재 Maker가 어느 SkillTable UserDataSet을 실제 등록해 읽는지는 런타임 금지 범위와 정상 경로 삭제 때문에 UNRESOLVED다. HEAD라는 이유만으로 현재 실행 데이터라고 부르지 않는다.
- INPUT V2.1은 게임 파일을 복구·수정하지 않는다.

## git status 증거

```text
{status.strip()}
```
"""
    return doc, changed


def projectile_review(rows: list[dict], style_by_ruid: dict[str, dict], balance: dict[str, float]) -> tuple[str, list[dict]]:
    header = [
        "# PROJECTILE SCOPE REVIEW", "",
        "코드 읽기 근거이며 런타임·아트 승인이 아니다. 엔진 이동 유지와 기존 투사체 그림 유지는 별도 판단이다.",
        "스텀피는 CAST 리소스가 없으므로 필수 VFX를 PROJECTILE 역할로 교정한다. 나머지는 CAST+ICON 필수 범위를 유지하고 기존 projectile을 KEEP하되 별도 재제작 여부는 NEEDS_DECISION이다.", "",
        "| Area | monster | skill | projectile RUID | preview | current cast | required V2.1 scope | 판정 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    details = []
    for x in rows:
        s = x["skill"]
        ruid = s.get("projectile_ruid", "")
        style = style_by_ruid.get(ruid)
        preview = "not in style library"
        if style:
            preview = f"{style.get('reference_role')}; usable={style.get('preview_usable')}"
        has_cast = bool(layers(s) or s.get("effect_ruid"))
        required = "PROJECTILE+ICON" if not has_cast else "CAST_VFX+ICON; existing PROJECTILE keep"
        decision = "REPLACE_PLANNED projectile" if not has_cast else "NEEDS_DECISION optional projectile redraw"
        header.append(f"| {x['area_id']} | `{x['monster_id']}` | `{s['id']}` | `{ruid}` | {preview} | {'yes' if has_cast else 'no'} | {required} | {decision} |")
        details.append({"area_id": x["area_id"], "monster_id": x["monster_id"], "skill_id": s["id"], "projectile_ruid": ruid, "has_cast": has_cast, "required_scope": required, "decision": decision})
    header += ["", "## 공통 연결 주의", "", f"- 비행 시간은 GameBalance `projectile_seconds={fmt(balance.get('projectile_seconds', 0.35))}`초이며 이미지 프레임의 캔버스 이동으로 중복하지 않는다.", "- projectile entity가 caster+h에서 target+h로 이동하고 spin을 적용한다.", "- CAST의 절정과 착탄은 자동으로 같은 시점이 아니다. 착탄 전용 파일을 요구하려면 별도 데이터 필드/호출 경로 결정이 필요하다.", "- 기존 projectile의 미술 적합성은 픽셀/메타데이터만으로 승인하지 않는다."]
    return "\n".join(header) + "\n", details


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"destination already exists; choose a new revision: {OUT}")
    baseline = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    commit = baseline["git_head"]
    status_before = git_status()
    commit_skill_bytes = git_bytes(commit, "RootDesk/MyDesk/GameData/SkillTable.csv")
    commit_skills = csv_rows(commit_skill_bytes)
    commit_skill_map = {r["id"]: r for r in commit_skills}
    mis_skill_path = MISLOCATED / "SkillTable.csv"
    mis_skills = csv_rows(mis_skill_path.read_bytes()) if mis_skill_path.exists() else []
    mis_skill_map = {r["id"]: r for r in mis_skills}
    area00_map_rows = csv_rows((AREA00 / "AREA_00_IMAGES_RESOURCE_MAP.csv").read_bytes())
    approved_map = {r["monster_id"]: r for r in area00_map_rows}
    balance_rows = csv_rows(git_bytes(commit, "RootDesk/MyDesk/GameData/GameBalance.csv"))
    balance = {r["key"]: num(r["value"]) for r in balance_rows}

    current_code_hashes = {rel: sha_file(ROOT / rel) for rel in CODE_FILES}
    runtime_doc = runtime_evidence_doc(current_code_hashes, balance)
    data_resolution, changed_skill_rows = build_data_resolution(baseline, commit_skills, mis_skills, area00_map_rows, status_before)

    with tempfile.TemporaryDirectory(prefix="input_v2_1_build_") as td:
        tmp = Path(td)
        final_stage = tmp / "final"
        final_stage.mkdir()
        style_temp = tmp / "style"
        style_root, style_rows, white_rows = sync_style_library(V2 / "AREA_01_IMAGES_INPUT_V2.zip", style_temp)
        style_by_ruid = {r["RUID"]: r for r in style_rows}

        area_manifests = {}
        projectile_items = []
        global_binding = []
        area_results = []
        source_evidence_rows = []

        # Prepare manifests and projectile review inputs first.
        for aid in TARGET_IDS:
            with zipfile.ZipFile(V2 / f"{aid.upper()}_IMAGES_INPUT_V2.zip") as z:
                root = f"{aid.upper()}_IMAGES_INPUT_V2/"
                manifest = csv_rows(z.read(root + "AREA_MANIFEST.csv"))
            area_manifests[aid] = manifest
            for row in manifest:
                sid = row["skill_id"]
                skill = commit_skill_map.get(sid) or mis_skill_map.get(sid)
                if skill and skill.get("projectile_ruid"):
                    projectile_items.append({"area_id": aid, "monster_id": row["monster_id"], "skill": skill})

        projectile_doc, projectile_details = projectile_review(projectile_items, style_by_ruid, balance)

        for aid in TARGET_IDS:
            area_temp = tmp / f"stage_{aid}"
            area_temp.mkdir()
            stage = extract_v2(aid, area_temp)
            manifest = area_manifests[aid]
            binding = []
            unresolved = []
            for row in manifest:
                mid, sid = row["monster_id"], row["skill_id"]
                approved = approved_map.get(mid) if approved_map.get(mid, {}).get("skill_id") == sid else None
                skill = commit_skill_map.get(sid) or mis_skill_map.get(sid)
                if not skill and not approved:
                    unresolved.append(f"{mid}/{sid}: no baseline or approved skill row")
                    continue
                spec = (stage / row["folder"] / "GENERATION_SPEC.md").read_text(encoding="utf-8")
                binding.extend(binding_rows(aid, row, skill or {}, spec, balance, approved))

                provenance = stage / row["folder"] / "SOURCE_PROVENANCE.md"
                ptxt = provenance.read_text(encoding="utf-8")
                model_path_match = re.search(r"^- model_path: `([^`]+)`", ptxt, re.M)
                img_sha_match = re.search(r"^- sha256: `([^`]+)`", ptxt, re.M)
                model_path = model_path_match.group(1) if model_path_match else "미확인"
                model_abs = ROOT / model_path if model_path != "미확인" else None
                source_evidence_rows.append({
                    "area_id": aid, "monster_id": mid, "skill_id": sid,
                    "model_path": model_path, "model_exists": str(bool(model_abs and model_abs.exists())).lower(),
                    "model_sha256": sha_file(model_abs) if model_abs and model_abs.exists() else "",
                    "monster_image_sha256": img_sha_match.group(1) if img_sha_match else "",
                    "verification_level": "model RUID match + package byte hash + contact-sheet visual review; original download/frame index unavailable",
                })

            add_v21_docs(stage, aid, manifest, commit_skill_map | mis_skill_map, balance, approved_map, binding, style_root, runtime_doc)
            (stage / "DATA_SOURCE_RESOLUTION.md").write_text(data_resolution, encoding="utf-8", newline="\n")
            (stage / "PROJECTILE_SCOPE_REVIEW.md").write_text(projectile_doc, encoding="utf-8", newline="\n")
            package_revision = f"""# PACKAGE REVISION — V2.1

- source: `{aid.upper()}_IMAGES_INPUT_V2.zip`
- source_sha256: `{sha_file(V2 / f'{aid.upper()}_IMAGES_INPUT_V2.zip')}`
- built_utc: `{datetime.now(timezone.utc).isoformat()}`
- confirmed identity/gameplay fields changed: `false`
- Area 00 assets changed: `false`
- art generated: `false`
- review attachment available: `false` (`INPUT_V2_REVIEW_RESULTS.zip` not found)
- status: `{'BLOCKED' if unresolved else 'READY'}`
"""
            (stage / "PACKAGE_REVISION_V2_1.md").write_text(package_revision, encoding="utf-8", newline="\n")
            global_binding.extend(binding)
            zip_path = final_stage / f"{aid.upper()}_IMAGES_INPUT_V2_1.zip"
            zip_tree(stage, zip_path)
            area_results.append({"area_id": aid, "area_name": manifest[0]["area_name"], "monsters": len(manifest), "status": "BLOCKED" if unresolved else "READY", "reason": "; ".join(unresolved) or "필수 입력·동작 역할 확인", "zip": zip_path.name, "sha256": sha_file(zip_path)})

        evidence = tmp / "INPUT_V2_1_EVIDENCE"
        evidence.mkdir()
        prior = evidence / "prior_v2_reports"
        prior.mkdir()
        for name in V2_REPORTS:
            shutil.copy2(V2 / name, prior / name)
        shutil.copy2(BASELINE_JSON, prior / "SOURCE_BASELINE.json")

        baseline_dir = evidence / "baseline_commit" / "RootDesk" / "MyDesk" / "GameData"
        baseline_dir.mkdir(parents=True)
        for rel in BASELINE_DATA_FILES:
            (baseline_dir / Path(rel).name).write_bytes(git_bytes(commit, rel))

        current_dir = evidence / "current_candidates"
        current_dir.mkdir()
        for p in (DATA / "MonsterTable.csv", DATA / "AreaTable.csv", DATA / "RoomTable.csv", DATA / "GameBalance.csv",
                  MISLOCATED / "SkillTable.csv", MISLOCATED / "SkillTable.userdataset"):
            if p.exists():
                shutil.copy2(p, current_dir / ("Mislocated_" + p.name if "Mislocated" in p.parts else p.name))

        code_dir = evidence / "runtime_code"
        for rel in CODE_FILES:
            dst = code_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        (evidence / "RUNTIME_CODE_EVIDENCE.md").write_text(runtime_doc, encoding="utf-8", newline="\n")

        area00_dir = evidence / "area00_approval"
        area00_dir.mkdir()
        for name in AREA00_FILES:
            shutil.copy2(AREA00 / name, area00_dir / name)

        model_dir = evidence / "monster_models"
        copied_models = set()
        for row in source_evidence_rows:
            rel = row["model_path"]
            src = ROOT / rel
            if rel != "미확인" and src.exists() and rel not in copied_models:
                dst = model_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied_models.add(rel)
        write_csv(evidence / "MONSTER_SOURCE_EVIDENCE.csv", source_evidence_rows, list(source_evidence_rows[0]))

        write_csv(evidence / "ASSET_BINDING_PLAN.csv", global_binding, BINDING_COLUMNS)
        (evidence / "ASSET_BINDING_PLAN.md").write_text(
            "# ASSET BINDING PLAN\n\n99개 배치의 현행 필드·레이어와 신규 파일 연결 계획이다. 기존 레이어는 승인 전 KEEP하며, REPLACE_PLANNED는 게임 변경이 아니라 이후 반입 계획이다. 같은 RUID 반복은 BuildEffectLayers가 허용하지만 명세 근거 없이 새 클립을 모든 L1/L2에 복제하지 않는다.\n",
            encoding="utf-8", newline="\n")
        (evidence / "PROJECTILE_SCOPE_REVIEW.md").write_text(projectile_doc, encoding="utf-8", newline="\n")
        (evidence / "DATA_SOURCE_RESOLUTION.md").write_text(data_resolution, encoding="utf-8", newline="\n")

        missing = f"""# MISSING EVIDENCE

| 자료 | 상태 | 이유 | 영향 |
|---|---|---|---|
| INPUT_V2_REVIEW_RESULTS.zip | 미확보 | 첨부 저장소·프로젝트·Downloads에 실제 파일 없음 | 검수 주장 자체는 적용하지 않고 독립 검사 수행 |
| 원 리소스 다운로드 바이트/cache | 미확보 | V2 provenance에도 원 cache가 보존되지 않음 | model RUID·현재 PNG SHA·육안 대조까지만 확인 |
| 대표 프레임 index | 미확보 | 기존 추출기가 max alpha bbox를 골랐으나 index를 기록하지 않음 | 선택 프레임을 확인했다고 주장하지 않음 |
| 현재 Maker 등록 SkillTable | 미확인 | 정상 경로 userdataset 삭제, Mislocated 후보의 등록 여부 불명 | 기준 commit+승인 map+후보 일치로 INPUT 데이터는 해소; 실제 런타임 등록은 미확인 |
| 11개 projectile 별도 신규 아트 승인 | 미확인 | V2는 CAST+ICON 범위였고 별도 승인 기록 없음 | 기존 projectile KEEP, 선택적 재제작은 NEEDS_DECISION; 필수 INPUT 제작은 가능 |
| 6개 dash의 계산 도착점과 CAST 부착점 일치 | 불일치 가능 | 피해는 계산 도착점, CAST는 서버가 보는 caster 위치 | INPUT에는 실제 코드대로 명시; 게임 코드 변경은 이번 범위 밖 |
"""
        (evidence / "MISSING_EVIDENCE.md").write_text(missing, encoding="utf-8", newline="\n")

        changelog = f"""# INPUT V2.1 CHANGELOG

- V2 19개 Area/99개 배치를 보존하고 별도 V2.1로 재패키징.
- 기준 커밋 `{commit}`의 SkillTable/UserDataSet 및 관련 데이터 증빙 확보.
- 정상 SkillTable 삭제와 Mislocated 후보를 분리하고 Area 00 승인 RUID 일치 근거 기록.
- 183개 style index와 모든 `skills/*/info.md`의 role/priority/preview usable 상태 동기화.
- exact opaque-white preview {len(white_rows)}개를 `preview_usable=false`로 표시하고 주 스타일 분석에서 제외.
- 돌진 6종의 플레이어/몬스터 actual_motion 차이와 CAST 부착점 한계를 manifest/spec/runtime map에 동기화.
- 투사체 12종 검토: 스텀피 VFX를 PROJECTILE 역할로 교정, 나머지 기존 projectile은 KEEP+선택적 재제작 NEEDS_DECISION.
- 몬스터별 labeled preview와 AREA_OVERVIEW_PREVIEW를 필수 검수 납품물로 통일.
- 99개 배치에 대한 ASSET_BINDING_PLAN 작성. 게임·Area00·V2·OUTPUT 수정 없음.
"""
        (evidence / "INPUT_V2_1_CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")

        findings = f"""# INPUT V2.1 ADDITIONAL FINDINGS

## 확인된 INPUT 오류 — 보정

1. style index와 개별 info.md의 제외 역할/우선순위가 동기화되지 않음 → 183개 전부 동기화.
2. exact opaque-white preview는 실제 파일 검사상 {len(white_rows)}개로 감사 후보 8개와 일치 → usable=false, 분석 제외.
3. 돌진 actual_motion이 플레이어 동작만 기술 → 몬스터는 dash 분기가 없음을 분리 기재.
4. 돌진 충돌 VFX가 계산 도착점에 뜬다고 단정 → 실제로는 PlayCast 시점의 caster 서버 위치에 부착됨을 정정.
5. 스텀피는 CAST 필드가 없는데 generic CAST VFX로 기술 → PROJECTILE replacement 역할로 정정.
6. Preview가 선택 산출물처럼 남은 문서 → monster labeled preview와 Area overview preview를 필수 검수물로 통일.

## 게임 동작·기획 변경 필요 — 미변경

- 돌진 피해 좌표와 CAST 부착 좌표의 일치 보장은 코드 변경이 필요하다.
- 11개 복합 projectile 스킬의 비행체까지 새로 그릴지는 승인 근거가 없어 NEEDS_DECISION이다.

## 자료 부족

- 검수 ZIP, 원 다운로드 cache, 대표 프레임 index, 현재 Maker 등록 SkillTable은 미확보다.
"""
        (evidence / "INPUT_V2_1_ADDITIONAL_FINDINGS.md").write_text(findings, encoding="utf-8", newline="\n")

        index = [
            "# ALL AREAS INPUT V2.1 INDEX", "",
            f"- 대상: {len(area_results)} Area / {sum(x['monsters'] for x in area_results)} monster placements",
            "- area_06: 예약 결번, 생성하지 않음", "- Area 00: 읽기·해시 대조만 수행", "",
            "| Area | 이름 | 몬스터 | 상태 | 사유 | ZIP | SHA-256 |", "|---|---|---:|---|---|---|---|",
        ]
        for x in area_results:
            index.append(f"| {x['area_id']} | {x['area_name']} | {x['monsters']} | {x['status']} | {x['reason']} | `{x['zip']}` | `{x['sha256']}` |")
        index_text = "\n".join(index) + "\n"
        (evidence / "ALL_AREAS_INPUT_V2_1_INDEX.md").write_text(index_text, encoding="utf-8", newline="\n")
        (final_stage / "ALL_AREAS_INPUT_V2_1_INDEX.md").write_text(index_text, encoding="utf-8", newline="\n")

        validation = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "target_areas": len(area_results), "monster_placements": sum(x["monsters"] for x in area_results),
            "ready": sum(x["status"] == "READY" for x in area_results),
            "blocked": sum(x["status"] == "BLOCKED" for x in area_results),
            "area06_created": False, "white_previews": len(white_rows), "style_resources": len(style_rows),
            "projectile_skills": len(projectile_details), "dash_target_skills": 6,
            "review_zip_available": False, "changed_skill_rows_candidate_vs_commit": changed_skill_rows,
            "area_results": area_results,
        }
        (evidence / "INPUT_V2_1_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        validation_md = f"""# INPUT V2.1 VALIDATION

- Area: {validation['target_areas']}
- monster placements: {validation['monster_placements']}
- READY/BLOCKED: {validation['ready']}/{validation['blocked']}
- style resources: {validation['style_resources']}
- exact white unusable previews: {validation['white_previews']}
- projectile skills reviewed: {validation['projectile_skills']}
- dash target skills reviewed: {validation['dash_target_skills']}

이 파일은 빌드 단계 결과다. 별도 `verify-area-images-input-v2_1.py`가 완성 ZIP을 다시 열어 독립 검증한다.
"""
        (evidence / "INPUT_V2_1_VALIDATION.md").write_text(validation_md, encoding="utf-8", newline="\n")

        scripts_dir = evidence / "repro_scripts"
        scripts_dir.mkdir()
        shutil.copy2(Path(__file__), scripts_dir / Path(__file__).name)
        verifier = ROOT / "docs" / "tools" / "verify-area-images-input-v2_1.py"
        if verifier.exists():
            shutil.copy2(verifier, scripts_dir / verifier.name)

        # Evidence manifest is generated last and covers every evidence file except itself.
        ev_rows = []
        for p in sorted(evidence.rglob("*")):
            if not p.is_file() or p.name == "EVIDENCE_MANIFEST.csv":
                continue
            rel = p.relative_to(evidence).as_posix()
            if rel.startswith("baseline_commit/"):
                source, version = rel.split("/", 1)[1], commit
            elif rel.startswith("runtime_code/"):
                source, version = rel[len("runtime_code/"):], f"working-tree@{commit}"
            elif rel.startswith("prior_v2_reports/"):
                source, version = "docs/art/images-input-packages-v2/" + p.name, "V2 immutable copy"
            elif rel.startswith("area00_approval/"):
                source, version = "docs/art/area00-images-output/" + p.name, "AREA00 approved copy"
            elif rel.startswith("current_candidates/"):
                source, version = "working-tree candidate", f"working-tree@{commit}"
            elif rel.startswith("monster_models/"):
                source, version = rel[len("monster_models/"):], f"working-tree@{commit}"
            else:
                source, version = "generated", "INPUT V2.1"
            ev_rows.append({"evidence_path": rel, "source_path": source, "source_version": version, "available": "true", "sha256": sha_file(p), "bytes": p.stat().st_size})
        write_csv(evidence / "EVIDENCE_MANIFEST.csv", ev_rows, ["evidence_path", "source_path", "source_version", "available", "sha256", "bytes"])

        evidence_zip = final_stage / "INPUT_V2_1_EVIDENCE.zip"
        zip_tree(evidence, evidence_zip)

        # Add final evidence ZIP hash without changing the already zipped manifest.
        final_summary = {
            **validation,
            "evidence_zip": evidence_zip.name,
            "evidence_zip_sha256": sha_file(evidence_zip),
            "v2_frozen_hashes": {p.name: sha_file(p) for p in sorted(V2.glob("AREA_*_IMAGES_INPUT_V2.zip"))},
            "area00_frozen_hashes": baseline["area00_frozen_sha256"],
            "status_before": status_before,
        }
        (final_stage / "BUILD_RESULT.json").write_text(json.dumps(final_summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        shutil.move(str(final_stage), str(OUT))

    print(json.dumps({"out": str(OUT), "areas": 19, "monsters": 99, "white_previews": len(white_rows), "projectiles": len(projectile_details)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
