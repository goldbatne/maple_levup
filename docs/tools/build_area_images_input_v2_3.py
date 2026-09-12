#!/usr/bin/env python3
"""Expand V2.2 packages to complete visual-asset production scope in V2.3.

No images, OUTPUT artifacts, game files, resources, RUIDs, or prior packages are
modified. Every V2.3 package is derived from one immutable V2.2 ZIP.
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
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/art/images-input-packages-v2_2"
OUT = ROOT / "docs/art/images-input-packages-v2_3"
BASELINE = ROOT / "docs/art/images-input-packages-v2/SOURCE_BASELINE.json"
AREA00_MAP = ROOT / "docs/art/area00-images-output/AREA_00_IMAGES_RESOURCE_MAP.csv"
MISLOCATED_SKILLS = ROOT / "Mislocated/MyDesk/GameData/SkillTable.csv"
TARGET_IDS = [f"area_{i:02d}" for i in range(1, 21) if i != 6]
STANDARD_ROLES = ["ICON", "CAST_VFX", "PROJECTILE", "HIT_VFX", "PERSISTENT_BUFF_VFX", "REFERENCE_VFX"]
STUMPY_ID = "s_mon_stumpy"


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


def git_bytes(commit: str, rel: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{rel}"], cwd=ROOT)


def split(raw: str | None) -> list[str]:
    return [] if not raw else raw.split("|")


def fmt(value: str | float | int | None) -> str:
    if value is None or value == "":
        return "0"
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else str(number)
    except (ValueError, TypeError):
        return str(value)


def skill_type(skill: dict[str, str]) -> str:
    if skill.get("skill_kind") == "passive":
        return "패시브"
    if skill.get("skill_kind") == "defense":
        return "버프"
    return "액티브"


def layer_details(skill: dict[str, str]) -> list[dict[str, str]]:
    ruids = split(skill.get("layer_ruids"))
    fields = {
        "type": split(skill.get("layer_types")), "style": split(skill.get("layer_styles")),
        "delay": split(skill.get("layer_delays")), "duration": split(skill.get("layer_durations")),
        "scale": split(skill.get("layer_scales")), "offset_x": split(skill.get("layer_offsets_x")),
        "offset_y": split(skill.get("layer_offsets_y")), "drift_x": split(skill.get("layer_drifts_x")),
        "drift_y": split(skill.get("layer_drifts_y")),
    }
    defaults = {"type": "sprite", "style": "burst", "delay": "0", "duration": "0.4", "scale": "1", "offset_x": "0", "offset_y": "0", "drift_x": "0", "drift_y": "0"}
    result = []
    for index, ruid in enumerate(ruids):
        row = {"ruid": ruid}
        for key, values in fields.items():
            row[key] = values[index] if index < len(values) and values[index] else defaults[key]
        result.append(row)
    return result


def layer_text(skill: dict[str, str]) -> str:
    rows = layer_details(skill)
    if not rows:
        return "none"
    return "; ".join(
        f"L{i + 1}:{row['ruid']} {row['type']}/{row['style']} delay={row['delay']}s duration={row['duration']}s "
        f"scale={row['scale']} offset=({row['offset_x']},{row['offset_y']})wu drift=({row['drift_x']},{row['drift_y']})wu/s"
        for i, row in enumerate(rows)
    )


def remove_section(text: str, title: str) -> str:
    return re.sub(rf"(?ms)^## {re.escape(title)}\n.*?(?=^## |\Z)", "", text).rstrip() + "\n"


def replace_section(text: str, title: str, body: str) -> str:
    return remove_section(text, title).rstrip() + f"\n\n## {title}\n\n{body.strip()}\n"


def parse_profile(spec: str) -> tuple[int, int, str]:
    match = re.search(r"(?:VFX|REFERENCE_VFX|PROJECTILE):\s*(\d+) frames, 각 (\d+)×(\d+) RGBA PNG, (?:약 |정확히 )?([0-9.]+) sec/frame", spec)
    if not match:
        raise RuntimeError("output profile missing")
    if match.group(2) != match.group(3):
        raise RuntimeError("non-square profile")
    return int(match.group(1)), int(match.group(2)), match.group(4)


def zip_tree(root: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(root.parent).as_posix())


def extract_v22(aid: str, parent: Path) -> Path:
    source = SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_2.zip"
    with zipfile.ZipFile(source) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"CRC error in {source.name}: {bad}")
        archive.extractall(parent)
    old = parent / f"{aid.upper()}_IMAGES_INPUT_V2_2"
    new = parent / f"{aid.upper()}_IMAGES_INPUT_V2_3"
    old.rename(new)
    return new


def approved_files(stage: Path, skill_id: str) -> str:
    reuse = stage / "approved_reuse" / "AREA_00"
    if not reuse.exists():
        return "approved_reuse/AREA_00 (see AREA_00_REUSE_MANIFEST.md)"
    files = [p.relative_to(stage).as_posix() for p in sorted(reuse.rglob("*.png")) if skill_id in p.name]
    return "|".join(files) if files else "approved_reuse/AREA_00 (see AREA_00_REUSE_MANIFEST.md)"


def full_scope_rows(aid: str, manifest_row: dict[str, str], skill: dict[str, str], spec: str,
                    approved: dict[str, str] | None, stage: Path, balance: dict[str, float]) -> list[dict]:
    frames, canvas, frame_seconds = parse_profile(spec)
    sid, mid, order = skill["id"], manifest_row["monster_id"], f"{int(manifest_row['work_order']):03d}"
    passive = skill_type(skill) == "패시브"
    cast_layers = layer_details(skill)
    cast_field = "layer_ruids" if cast_layers else ("effect_ruid" if skill.get("effect_ruid") else "none")
    cast_exists = not passive and cast_field != "none"
    projectile_exists = bool(skill.get("projectile_ruid"))
    base = {
        "area_id": aid, "area_name": manifest_row["area_name"], "work_order": order,
        "monster_id": mid, "monster_name": manifest_row["monster_name"],
        "skill_id": sid, "skill_name": manifest_row["skill_name"], "skill_type": manifest_row["skill_type"],
        "pivot": "normalized (0.5,0.5); no autocrop/recenter",
        "targeting_range": manifest_row.get("targeting_range", "n/a"),
        "impact_radius": manifest_row.get("impact_radius", "n/a"),
        "impact_delay": manifest_row.get("impact_delay", "n/a"),
    }
    rows = []
    for role in STANDARD_ROLES:
        row = {**base, "effect_role": role, "current_use": "false", "current_field_or_layer": "none",
               "current_resource": "", "production_decision": "NO_RUNTIME_ROLE", "required_file_set": "none",
               "frame_count": "0", "canvas": "n/a", "frame_seconds": "n/a", "total_seconds": "n/a",
               "playback_mode": "n/a", "direction_and_engine_motion": "n/a", "future_target": "none",
               "consolidation_strategy": "n/a", "runtime_use": "false", "unresolved": "none",
               "evidence": "SkillTable visual fields + PlayerAttack/MonsterAttack/SkillEffect code"}
        if role == "ICON":
            row.update({
                "current_use": "true", "current_field_or_layer": "icon_ruid", "current_resource": skill.get("icon_ruid", ""),
                "production_decision": "AREA00_APPROVED_REUSE" if approved else "NEW_ART",
                "required_file_set": approved_files(stage, sid) if approved else f"ICON/{order}_{mid}_{sid}_ICON.png",
                "frame_count": "1", "canvas": "256x256 RGBA", "frame_seconds": "static", "total_seconds": "static",
                "playback_mode": "static", "direction_and_engine_motion": "none", "future_target": "icon_ruid",
                "runtime_use": "ui", "evidence": "SkillTable.icon_ruid; Area00 resource map/hash" if approved else "SkillTable.icon_ruid",
            })
        elif role == "CAST_VFX" and (cast_exists or (approved and not passive)):
            current_resource = layer_text(skill) if cast_layers else skill.get("effect_ruid", "")
            row.update({
                "current_use": "true", "current_field_or_layer": cast_field if cast_field != "none" else "approved layer_ruids",
                "current_resource": current_resource or (approved.get("animationclip_ruid", "") if approved else ""),
                "production_decision": "AREA00_APPROVED_REUSE" if approved else "NEW_ART",
                "required_file_set": approved_files(stage, sid) if approved else f"CAST/{order}_{mid}_{sid}_CAST_F00.png..._CAST_F{frames - 1:02d}.png",
                "frame_count": approved.get("frame_count", str(frames)) if approved else str(frames),
                "canvas": approved.get("canvas_rgba", f"{canvas}x{canvas} RGBA") if approved else f"{canvas}x{canvas} RGBA",
                "frame_seconds": approved.get("frame_seconds", frame_seconds) if approved else frame_seconds,
                "total_seconds": approved.get("total_seconds", fmt(frames * float(frame_seconds))) if approved else fmt(frames * float(frame_seconds)),
                "playback_mode": "approved existing" if approved else "non-loop one-shot",
                "direction_and_engine_motion": "SkillEffect applies FlipX for directional attacks; delayed layer samples caster position at SpawnLayer execution; map entity then applies drift",
                "future_target": "approved existing layer_ruids" if approved else cast_field,
                "consolidation_strategy": "AREA00 approved mapping unchanged" if approved else ("COMPOSITE_BAKED_ONE_CLIP: preserve L1..Ln relative delay/offset/drift rhythm inside one accepted local-canvas clip; final layer metadata becomes one primary layer after approval" if len(cast_layers) > 1 else "ONE_TO_ONE_PRIMARY_CLIP"),
                "runtime_use": "true", "evidence": "SkillTable layer/effect fields; SkillEffect.PlayCast/SpawnLayer",
            })
        elif role == "PROJECTILE" and projectile_exists:
            row.update({
                "current_use": "true", "current_field_or_layer": "projectile_ruid",
                "current_resource": skill["projectile_ruid"], "production_decision": "NEW_ART",
                "required_file_set": f"PROJECTILE/{order}_{mid}_{sid}_PROJECTILE_F00.png..._PROJECTILE_F03.png",
                "frame_count": "4", "canvas": f"{canvas}x{canvas} RGBA", "frame_seconds": "0.08",
                "total_seconds": "0.32", "playback_mode": "non-loop complete playback within 0.35s entity lifetime",
                "direction_and_engine_motion": "art direction-neutral/local form only; engine translates caster+h to target+h and applies ZRotation; no PROJECTILE FlipX or travel-direction alignment",
                "future_target": "projectile_ruid", "consolidation_strategy": "independent from CAST; do not merge",
                "runtime_use": "true", "unresolved": "import must author AnimationClip non-loop at 0.08s/frame; Maker runtime not run",
                "evidence": "SkillTable.projectile_ruid; SkillEffect.mlua:149-194; SkillProjectile.mlua:39-81; GameBalance projectile_seconds=0.35",
            })
        elif role == "HIT_VFX":
            row.update({"unresolved": "none; no dedicated hit/impact visual field or Spawn call in current common projectile path", "evidence": "PlayerAttack.ResolveThrowHit; MonsterAttack.ResolveThrowHit; SkillEffect has no hit asset argument"})
        elif role == "PERSISTENT_BUFF_VFX":
            row.update({"unresolved": "none; defense mechanics may persist but current visual is one-shot CAST only", "evidence": "MonsterAttack defense branch + SkillEffect.PlayCast; no persistent visual entity field"})
        elif role == "REFERENCE_VFX" and passive:
            current_reference = layer_text(skill) if cast_layers else (skill.get("effect_ruid") or "INPUT design reference")
            row.update({
                "current_use": "input_reference_only", "current_field_or_layer": "reference source; not runtime field",
                "current_resource": current_reference, "production_decision": "NEW_ART",
                "required_file_set": f"REFERENCE/{order}_{mid}_{sid}_REFERENCE_F00.png..._REFERENCE_F{frames - 1:02d}.png",
                "frame_count": str(frames), "canvas": f"{canvas}x{canvas} RGBA", "frame_seconds": frame_seconds,
                "total_seconds": fmt(frames * float(frame_seconds)), "playback_mode": "preview-only non-loop",
                "direction_and_engine_motion": "preview only; no engine motion/FlipX contract",
                "future_target": "none", "consolidation_strategy": "preview/reference only; never auto-import as CAST",
                "runtime_use": "false", "evidence": "passive execution has no PlayCast; V2.2 REFERENCE_VFX scope",
            })
        rows.append(row)
    return rows


def required_roles(rows: list[dict]) -> tuple[str, str, str]:
    selected = [row for row in rows if row["production_decision"] != "NO_RUNTIME_ROLE"]
    roles = "|".join(row["effect_role"] for row in selected)
    targets = "|".join(row["future_target"] for row in selected)
    decisions = "|".join(row["production_decision"] for row in selected)
    return roles, targets, decisions


def scope_markdown(rows: list[dict], title: str) -> str:
    lines = [f"# {title}", "", "| role | current | production | files | timing | future target | unresolved |", "|---|---|---|---|---|---|---|"]
    for row in rows:
        timing = f"{row['frame_count']}f / {row['canvas']} / {row['frame_seconds']} / {row['playback_mode']}"
        lines.append(f"| {row['effect_role']} | {row['current_use']} · {row['current_field_or_layer']} | {row['production_decision']} | `{row['required_file_set']}` | {timing} | `{row['future_target']}` | {row['unresolved']} |")
    return "\n".join(lines) + "\n"


def update_spec(path: Path, scope: list[dict], row: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    text = remove_section(text, "V2.2 현행 런타임·납품 계약")
    selected = [item for item in scope if item["production_decision"] != "NO_RUNTIME_ROLE"]
    output = []
    for item in selected:
        if item["effect_role"] == "ICON":
            output.append(f"- ICON: {item['production_decision']} / {item['required_file_set']} / {item['canvas']}")
        else:
            output.append(f"- {item['effect_role']}: {item['production_decision']} / {item['required_file_set']} / {item['frame_count']} frames × {item['canvas']} / {item['frame_seconds']}s per frame / {item['playback_mode']}")
    text = replace_section(text, "출력 프로필", "\n".join(output) + "\n- 역할별 파일을 섞지 않는다. HIT/PERSISTENT 역할 없음 행은 신규 제작하지 않는다.")
    roles, targets, decisions = required_roles(scope)
    current = [
        f"- required_roles: `{roles}`", f"- production_decisions: `{decisions}`",
        f"- future_targets: `{targets}`", "- production_ready: `READY`",
        "- import_ready: `NOT_READY_ASSETS_NOT_GENERATED`", "",
        "### Role inventory", "",
    ]
    for item in scope:
        current.append(f"- {item['effect_role']}: current={item['current_use']}; decision={item['production_decision']}; field={item['current_field_or_layer']}; files={item['required_file_set']}; target={item['future_target']}")
    current += [
        "", "### Shared constraints", "",
        "- CAST와 PROJECTILE은 독립 파일 세트다. 같은 VFX 한 세트로 합치지 않는다.",
        "- PROJECTILE은 4×0.08=0.32초 non-loop로 0.35초 수명 안에 완주하며 엔진 이동·ZRotation을 이미지 안에서 중복하지 않는다.",
        "- 전용 HIT/PERSISTENT 시각 호출이 없으므로 해당 파일을 만들지 않는다.",
        "- 복수 CAST 레이어 통합은 기존 delay/offset/drift의 상대 리듬을 한 로컬 캔버스 clip에 베이크한다. 원본 레이어 정보는 ASSET_BINDING_PLAN에 남긴다.",
        "- targeting_range와 impact_radius는 별개이며 이미지로 조준 거리 전체를 피해 범위처럼 표현하지 않는다.",
        "- PREVIEW/labeled_preview.png와 Area overview는 필수 검수물이고 별도 contact sheet만 선택이다.",
    ]
    text = replace_section(text, "V2.3 전체 아트 제작 계약", "\n".join(current))
    path.write_text(text, encoding="utf-8", newline="\n")


def runtime_role_doc(row: dict[str, str], scope: list[dict]) -> str:
    roles, targets, decisions = required_roles(scope)
    text = scope_markdown(scope, f"Runtime Role Map — {row['monster_id']} / {row['skill_id']} — V2.3")
    text += f"""
## Authoritative contract

- required_roles: `{roles}`
- production_decisions: `{decisions}`
- future_targets: `{targets}`
- confirmed design effect preserved: {row['actual_effect']}
- runtime_effect preserved: {row['runtime_effect']}
- runtime_motion preserved: {row['runtime_motion']}
- targeting_range={row['targeting_range']} / impact_radius={row['impact_radius']} / impact_delay={row['impact_delay']} / max_targets={row['max_targets']}

No role marked `NO_RUNTIME_ROLE` may be generated merely because it appears in the inventory. Runtime import remains separate from production readiness.
"""
    return text


def output_requirements(scope: list[dict]) -> list[dict]:
    return [{
        "area_id": row["area_id"], "work_order": row["work_order"], "monster_id": row["monster_id"],
        "skill_id": row["skill_id"], "effect_role": row["effect_role"],
        "required": "true" if row["production_decision"] != "NO_RUNTIME_ROLE" else "false",
        "production_decision": row["production_decision"], "required_file_set": row["required_file_set"],
        "frame_count": row["frame_count"], "canvas": row["canvas"], "frame_seconds": row["frame_seconds"],
        "total_seconds": row["total_seconds"], "playback_mode": row["playback_mode"],
        "runtime_use": row["runtime_use"], "future_target": row["future_target"], "unresolved": row["unresolved"],
    } for row in scope]


def binding_plan(scope: list[dict]) -> list[dict]:
    return [{
        "area_id": row["area_id"], "monster_id": row["monster_id"], "skill_id": row["skill_id"],
        "effect_role": row["effect_role"], "current_use": row["current_use"],
        "current_field_or_layer": row["current_field_or_layer"], "current_resource": row["current_resource"],
        "decision": row["production_decision"], "generation_required": "true" if row["production_decision"] == "NEW_ART" else "false",
        "approved_reuse": "true" if row["production_decision"] == "AREA00_APPROVED_REUSE" else "false",
        "required_file_set": row["required_file_set"], "future_target": row["future_target"],
        "frame_contract": f"{row['frame_count']}|{row['canvas']}|{row['frame_seconds']}|{row['total_seconds']}|{row['playback_mode']}",
        "runtime_use": row["runtime_use"], "direction_and_engine_motion": row["direction_and_engine_motion"],
        "pivot": row["pivot"], "consolidation_strategy": row["consolidation_strategy"],
        "targeting_range": row["targeting_range"], "impact_radius": row["impact_radius"],
        "impact_delay": row["impact_delay"], "evidence": row["evidence"], "unresolved": row["unresolved"],
    } for row in scope]


def manifest_md(rows: list[dict]) -> str:
    lines = [
        "# AREA MANIFEST — V2.3", "",
        "FULL_ART_SCOPE.csv와 OUTPUT_REQUIREMENTS.csv가 역할별 제작 범위 원장이다. 확정 기획/런타임 수치는 V2.2에서 변경하지 않았다.", "",
        "| order | monster | skill | roles | decisions | production | import | runtime |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['work_order']} | `{row['monster_id']}` | `{row['skill_id']}` | {row['required_roles']} | {row['production_decisions']} | {row['production_ready']} | {row['import_ready']} | {row['runtime_validation']} |")
    return "\n".join(lines) + "\n"


def write_common_docs(stage: Path, aid: str, area_name: str) -> None:
    upper = aid.upper()
    naming = f"""# Output Naming Spec — V2.3

Output root: `{upper}_IMAGES_OUTPUT/`

- CAST: `NNN_[monster_id]_[skill_id]_CAST_F00.png` ...
- PROJECTILE: `NNN_[monster_id]_[skill_id]_PROJECTILE_F00.png` ...
- REFERENCE: `NNN_[monster_id]_[skill_id]_REFERENCE_F00.png` ...
- ICON: `NNN_[monster_id]_[skill_id]_ICON.png`
- HIT/PERSISTENT files are forbidden unless FULL_ART_SCOPE marks the role NEW_ART. Current V2.3 marks none.
- Each role uses a separate folder and frame sequence. CAST and PROJECTILE must not share a generic VFX filename.
- `PREVIEW/labeled_preview.png` and root `AREA_OVERVIEW_PREVIEW.png` are mandatory review files.
- A separate contact sheet is optional and cannot replace mandatory previews or frame-separated PNGs.
- SOURCE_SHEET and split coordinates are retained if a source sheet was used; no autocrop/recenter.
"""
    format_doc = f"""# Output Format Spec — V2.3

- `FULL_ART_SCOPE.csv` defines every actual/new/reused/absent role; `OUTPUT_REQUIREMENTS.csv` mirrors it.
- Primary art delivery is frame-separated RGBA PNG. Same role means identical canvas/pivot/scale.
- CAST uses the existing skill profile recorded in GENERATION_SPEC.
- Every actual PROJECTILE is newly produced as 4 frames × 0.08s = 0.32s non-loop within unchanged 0.35s entity life. Stumpy remains this exact contract.
- PROJECTILE artwork is direction-neutral and does not duplicate engine translation/ZRotation. Current code has no PROJECTILE FlipX/travel alignment.
- ICON is 256×256 RGBA. Passive REFERENCE is preview-only and runtime_use=false.
- No dedicated HIT/PERSISTENT visual path exists; do not generate those roles.
- targeting_range is not impact_radius. Do not depict target-search range as impact damage coverage.
- PACKAGE_VALIDATION/PRODUCTION_READY/IMPORT_READY/RUNTIME_VALIDATION/ART_APPROVAL remain separate.
"""
    (stage / "OUTPUT_NAMING_SPEC.md").write_text(naming, encoding="utf-8", newline="\n")
    (stage / "OUTPUT_FORMAT_SPEC.md").write_text(format_doc, encoding="utf-8", newline="\n")
    contract = f"""## V2.3 authoritative production scope

1. Read AREA_MANIFEST, FULL_ART_SCOPE, every GENERATION_SPEC/RUNTIME_ROLE_MAP, then OUTPUT_REQUIREMENTS.
2. Produce every `NEW_ART` role and copy every `AREA00_APPROVED_REUSE` role. Do not create `NO_RUNTIME_ROLE` files.
3. CAST and PROJECTILE are separate deliverables. The 11 formerly retained projectile artworks are now NEW_ART.
4. Existing RUIDs are evidence/current bindings, not permission to retain old art. Only the three exact Area 00 approved pairs are reuse exceptions.
5. Keep gameplay values and motion unchanged. Engine movement and art-local animation are separate.
6. Output to `{upper}_IMAGES_OUTPUT/`; frame-separated PNGs and mandatory previews are required.
7. An INPUT READY status is not import/runtime/art approval.
"""
    for name in ("README_START_HERE.md", "CHATGPT_IMAGES_MASTER_PROMPT.md"):
        path = stage / name
        old = path.read_text(encoding="utf-8")
        for title in ("V2.2 current delivery contract", "V2.3 authoritative production scope"):
            old = remove_section(old, title)
        old = old.replace("V2.2", "V2.3")
        path.write_text(old.rstrip() + "\n\n" + contract, encoding="utf-8", newline="\n")


def projectile_review(projectile_rows: list[dict]) -> str:
    lines = [
        "# PROJECTILE SCOPE REVIEW — V2.3", "",
        "All 12 actual monster projectile visual roles are NEW_ART. Engine movement is unchanged; existing projectile RUIDs remain evidence only until approved import.", "",
        "| Area | monster | skill | current RUID | new files | timing | targeting | impact | future target |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in projectile_rows:
        lines.append(f"| {row['area_id']} | `{row['monster_id']}` | `{row['skill_id']}` | `{row['current_resource']}` | `{row['required_file_set']}` | {row['frame_count']}×{row['frame_seconds']}={row['total_seconds']}s / {row['playback_mode']} | {row['targeting_range']} | {row['impact_radius']} after {row['impact_delay']}s | `{row['future_target']}` |")
    lines += ["", "- Stumpy has no CAST and remains PROJECTILE+ICON only.", "- The other 11 keep their CAST requirement and add an independent PROJECTILE requirement.", "- No HIT role is added because ResolveThrowHit has no visual asset field or effect spawn call."]
    return "\n".join(lines) + "\n"


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"destination exists: {OUT}")
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    skills = {row["id"]: row for row in csv_rows(git_bytes(baseline["git_head"], "RootDesk/MyDesk/GameData/SkillTable.csv"))}
    if MISLOCATED_SKILLS.exists():
        for row in csv_rows(MISLOCATED_SKILLS.read_bytes()):
            skills.setdefault(row["id"], row)
    approved_rows = csv_rows(AREA00_MAP.read_bytes())
    approved = {row["skill_id"]: row for row in approved_rows}
    balance = {row["key"]: float(row["value"]) for row in csv_rows((ROOT / "RootDesk/MyDesk/GameData/GameBalance.csv").read_bytes())}
    if balance["projectile_seconds"] != 0.35 or balance["projectile_hit_radius"] != 0.8:
        raise RuntimeError("projectile runtime contract changed; re-audit required")

    with tempfile.TemporaryDirectory(prefix="input_v2_3_build_") as td:
        temp = Path(td)
        final = temp / "final"
        final.mkdir()
        global_scope = []
        area_results = []
        source_hashes = {}
        style_hash = None

        for aid in TARGET_IDS:
            stage_parent = temp / aid
            stage_parent.mkdir()
            stage = extract_v22(aid, stage_parent)
            source_zip = SOURCE / f"{aid.upper()}_IMAGES_INPUT_V2_2.zip"
            source_hashes[source_zip.name] = sha_file(source_zip)
            manifest = csv_rows((stage / "AREA_MANIFEST.csv").read_bytes())
            area_scope = []
            for row in manifest:
                skill = skills.get(row["skill_id"])
                if not skill:
                    raise RuntimeError(f"skill source missing: {row['skill_id']}")
                spec_path = stage / row["folder"] / "GENERATION_SPEC.md"
                spec_text = spec_path.read_text(encoding="utf-8")
                pair_scope = full_scope_rows(aid, row, skill, spec_text, approved.get(row["skill_id"]), stage, balance)
                area_scope.extend(pair_scope)
                roles, targets, decisions = required_roles(pair_scope)
                row.update({
                    "required_roles": roles, "replacement_target_fields": targets,
                    "production_decisions": decisions, "production_ready": "READY",
                    "import_ready": "NOT_READY_ASSETS_NOT_GENERATED",
                })
                update_spec(spec_path, pair_scope, row)
                (stage / row["folder"] / "RUNTIME_ROLE_MAP.md").write_text(runtime_role_doc(row, pair_scope), encoding="utf-8", newline="\n")

            global_scope.extend(area_scope)
            write_csv(stage / "FULL_ART_SCOPE.csv", area_scope, list(area_scope[0]))
            requirements = output_requirements(area_scope)
            write_csv(stage / "OUTPUT_REQUIREMENTS.csv", requirements, list(requirements[0]))
            binding = binding_plan(area_scope)
            write_csv(stage / "ASSET_BINDING_PLAN.csv", binding, list(binding[0]))
            write_csv(stage / "AREA_MANIFEST.csv", manifest, list(manifest[0]))
            (stage / "AREA_MANIFEST.md").write_text(manifest_md(manifest), encoding="utf-8", newline="\n")
            write_common_docs(stage, aid, manifest[0]["area_name"])
            projectiles = [row for row in area_scope if row["effect_role"] == "PROJECTILE" and row["production_decision"] == "NEW_ART"]
            (stage / "PROJECTILE_SCOPE_REVIEW.md").write_text(projectile_review(projectiles), encoding="utf-8", newline="\n")
            (stage / "PACKAGE_STATUS_V2_3.md").write_text(f"""# Package status — {aid} / V2.3

| Axis | Status |
|---|---|
| PACKAGE_VALIDATION | PASS_BUILD |
| PRODUCTION_READY | READY |
| IMPORT_READY | NOT_READY_ASSETS_NOT_GENERATED |
| RUNTIME_VALIDATION | {'UNRESOLVED' if aid == 'area_20' else 'NOT_RUN'} |
| ART_APPROVAL | NOT_REVIEWED |
""", encoding="utf-8", newline="\n")
            (stage / "PACKAGE_REVISION_V2_3.md").write_text(f"""# PACKAGE REVISION — V2.3

- source: `{source_zip.name}`
- source_sha256: `{source_hashes[source_zip.name]}`
- built_utc: `{datetime.now(timezone.utc).isoformat()}`
- scope change: full actual visual-asset production coverage
- images/OUTPUT/resources/game files changed: `false`
""", encoding="utf-8", newline="\n")
            old_status = stage / "PACKAGE_STATUS_V2_2.md"
            old_revision = stage / "PACKAGE_REVISION_V2_2.md"
            history = stage / "history"
            history.mkdir(exist_ok=True)
            for old in (old_status, old_revision):
                if old.exists():
                    old.rename(history / old.name)
            old_conflicts = stage / "RUNTIME_CONFLICTS_V2_2.md"
            if old_conflicts.exists():
                conflict_text = old_conflicts.read_text(encoding="utf-8-sig")
                (stage / "RUNTIME_CONFLICTS_V2_3.md").write_text(
                    conflict_text.replace("V2.2", "V2.3"), encoding="utf-8", newline="\n"
                )
                old_conflicts.rename(history / old_conflicts.name)

            current_style_hash = sha_file(stage / "global_skill_style_library/STYLE_INDEX.csv")
            if style_hash is None:
                style_hash = current_style_hash
            elif current_style_hash != style_hash:
                raise RuntimeError("V2.2 style library divergence")

            zip_path = final / f"{aid.upper()}_IMAGES_INPUT_V2_3.zip"
            zip_tree(stage, zip_path)
            new_skills = len({row["skill_id"] for row in area_scope if row["production_decision"] == "NEW_ART"})
            area_results.append({
                "area_id": aid, "area_name": manifest[0]["area_name"], "monsters": len(manifest),
                "new_art_skills": new_skills, "new_sets": sum(row["production_decision"] == "NEW_ART" for row in area_scope),
                "package_validation": "PENDING_INDEPENDENT", "production_ready": "READY",
                "import_ready": "NOT_READY_ASSETS_NOT_GENERATED", "runtime_validation": "UNRESOLVED" if aid == "area_20" else "NOT_RUN",
                "art_approval": "NOT_REVIEWED", "zip": zip_path.name, "sha256": sha_file(zip_path),
            })

        write_csv(final / "FULL_ART_SCOPE.csv", global_scope, list(global_scope[0]))
        global_binding = binding_plan(global_scope)
        write_csv(final / "ASSET_BINDING_PLAN_V2_3.csv", global_binding, list(global_binding[0]))
        projectile_rows = [row for row in global_scope if row["effect_role"] == "PROJECTILE" and row["production_decision"] == "NEW_ART"]
        (final / "PROJECTILE_SCOPE_REVIEW_V2_3.md").write_text(projectile_review(projectile_rows), encoding="utf-8", newline="\n")

        new_counts = Counter(row["effect_role"] for row in global_scope if row["production_decision"] == "NEW_ART")
        reuse_counts = Counter(row["effect_role"] for row in global_scope if row["production_decision"] == "AREA00_APPROVED_REUSE")
        new_skills = {row["skill_id"] for row in global_scope if row["production_decision"] == "NEW_ART"}
        switched_projectiles = [row for row in projectile_rows if row["skill_id"] != STUMPY_ID]
        changelog = f"""# INPUT V2.3 CHANGELOG

- V2.2 19 packages remain untouched; V2.3 is a separate revision.
- Enumerated {len(global_scope)} role rows: 99 monster/skill pairs × {len(STANDARD_ROLES)} standard visual roles.
- Expanded 11 prior PROJECTILE KEEP items to NEW_ART. Stumpy remains PROJECTILE+ICON without invented CAST.
- Every actual projectile uses a separate 4×0.08=0.32s non-loop file set within unchanged 0.35s life.
- Preserved Area 00 approved reuse for exactly three pairs: s_mon_snail_dew_trail, s_mon_blue_snail, s_mon_slime.
- Passive ICON and REFERENCE_VFX remain production scope; REFERENCE runtime_use=false.
- Dedicated HIT/PERSISTENT visual roles remain NO_RUNTIME_ROLE because current code has no corresponding asset path.
- Multiple CAST layers use COMPOSITE_BAKED_ONE_CLIP, retaining the source layer timing/offset/drift recipe in ASSET_BINDING_PLAN.
- Game values, actual behavior, source monster images, style library, OUTPUT, resources, and game files were not changed.
"""
        (final / "INPUT_V2_3_CHANGELOG.md").write_text(changelog, encoding="utf-8", newline="\n")
        index = [
            "# ALL AREAS INPUT V2.3 INDEX", "",
            f"- target: {len(area_results)} Areas / 99 pairs / {len(new_skills)} skills requiring new art",
            f"- NEW_ART sets: {sum(new_counts.values())} ({', '.join(f'{k} {v}' for k, v in sorted(new_counts.items()))})",
            f"- AREA00 approved reuse sets: {sum(reuse_counts.values())} ({', '.join(f'{k} {v}' for k, v in sorted(reuse_counts.items()))})",
            "- Area 06: reserved; not created", "",
            "| Area | name | pairs | new-art skills | new sets | PACKAGE | PRODUCTION | IMPORT | RUNTIME | ART | ZIP | SHA-256 |",
            "|---|---|---:|---:|---:|---|---|---|---|---|---|---|",
        ]
        for row in area_results:
            index.append(f"| {row['area_id']} | {row['area_name']} | {row['monsters']} | {row['new_art_skills']} | {row['new_sets']} | {row['package_validation']} | {row['production_ready']} | {row['import_ready']} | {row['runtime_validation']} | {row['art_approval']} | `{row['zip']}` | `{row['sha256']}` |")
        (final / "ALL_AREAS_INPUT_V2_3_INDEX.md").write_text("\n".join(index) + "\n", encoding="utf-8", newline="\n")
        build = {
            "built_utc": datetime.now(timezone.utc).isoformat(), "areas": len(area_results), "pairs": 99,
            "scope_rows": len(global_scope), "new_art_skills": len(new_skills), "new_set_counts": dict(new_counts),
            "approved_reuse_counts": dict(reuse_counts), "switched_projectiles": len(switched_projectiles),
            "area06_created": False, "images_generated": False, "output_modified": False,
            "source_v2_2_hashes": source_hashes, "style_index_sha256": style_hash, "area_results": area_results,
        }
        (final / "BUILD_RESULT.json").write_text(json.dumps(build, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        shutil.move(str(final), str(OUT))

    print(json.dumps({"out": str(OUT), "areas": 19, "pairs": 99, "scope_rows": len(global_scope), "new_art_skills": len(new_skills), "new_sets": dict(new_counts)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
