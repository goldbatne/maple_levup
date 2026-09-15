from pathlib import Path
import csv
import datetime
import hashlib
import io
import json
import re
import zipfile

from rebuild_area00_command_system import (
    balanced_representatives,
    contact_board,
    decode,
    parse_skill_spec,
    sha,
)

BASE = Path(__file__).parent.parent / "images-input-packages"
COLLECTION = Path(__file__).parent
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def runtime_roles(data, folder):
    text = decode(data[folder + "/RUNTIME_ROLE_MAP.md"])
    match = re.search(r"required NEW_ART roles:\s*\*\*(.+?)\*\*", text)
    assert match
    return {part.strip() for part in match.group(1).split("|")}


def make_table(rows, specs, roles):
    lines = []
    for row in rows:
        need = roles[row["skill_id"]]
        outputs = []
        if "VFX" in need:
            outputs.append(f'{specs[row["skill_id"]]["frames"]}× VFX')
        if "ICON" in need:
            outputs.append("ICON 1")
        lines.append(
            f'| {int(row["work_order"]):03d} | {row["monster_name"]} / `{row["monster_id"]}` | '
            f'{row["skill_name"]} / `{row["skill_id"]}` | {row["skill_type"]} | '
            f'{" + ".join(outputs)} | `{row["folder"]}/DESIGN_REFERENCE_BRIEF.md` |'
        )
    return "\n".join(lines)


def make_prompt(area, area_name, rows, specs, roles, template):
    vfx_rows = [r for r in rows if "VFX" in roles[r["skill_id"]]]
    anchor = vfx_rows[0]
    total_vfx = sum(specs[r["skill_id"]]["frames"] for r in vfx_rows)
    icon_count = sum("ICON" in roles[r["skill_id"]] for r in rows)
    distribution = " + ".join(str(specs[r["skill_id"]]["frames"]) for r in vfx_rows)
    text = template.split("## 이 Area의 계산된 필수 수량")[0].rstrip() + "\n"
    text = text.replace("AREA 00", f"AREA {area}").replace("AREA_00", f"AREA_{area}")
    text = re.sub(r"^# AREA \d+ 신규 제작 실행 명령", f"# AREA {area} {area_name} 신규 제작 실행 명령", text, flags=re.M)
    text = re.sub(r"^- 대상: .*", f"- 대상: {len(rows)}스킬", text, flags=re.M)
    text = re.sub(r"^- 필수 VFX: 총 .*", f"- 필수 VFX: 총 {total_vfx}장의 frame-separated 256×256 RGBA PNG", text, flags=re.M)
    text = re.sub(r"^- 필수 ICON: .*", f"- 필수 ICON: 256×256 RGBA PNG {icon_count}장", text, flags=re.M)
    start = text.index("| 순번 | 몬스터 | 스킬 | 타입 | 필수 산출 | 실제 참조 brief |")
    end = text.index("\n\nmonster_id", start)
    header = "| 순번 | 몬스터 | 스킬 | 타입 | 필수 산출 | 실제 참조 brief |\n|---:|---|---|---|---|---|\n"
    text = text[:start] + header + make_table(rows, specs, roles) + text[end:]
    text = re.sub(
        r"먼저 `001 / m_snail / s_mon_snail_dew_trail`만 제작한다\.",
        f'먼저 `{int(anchor["work_order"]):03d} / {anchor["monster_id"]} / {anchor["skill_id"]}`만 제작한다.',
        text,
    )
    text = text.replace("002로 진행한다", "다음 스킬로 진행한다")
    text = re.sub(
        r"- 이슬·점액의 낮은 지면 흐름으로 읽히고 물 폭발이나 달팽이 캐릭터가 되지 않음",
        "- GENERATION_SPEC의 핵심 소재·방향·효과로 읽히며 공식 참조의 캐릭터·무기·고유 소재로 바뀌지 않음",
        text,
    )
    text = text.replace("002~005나 Area 전체 이미지를 생성하지 않는다", "나머지 스킬이나 Area 전체 이미지를 생성하지 않는다")
    text = text.replace("통과 후 002→005 순서로 한 스킬씩 진행한다", "통과 후 manifest 작업 순번대로 한 스킬씩 진행한다")
    text = re.sub(r"다섯 몬스터·다섯 스킬", "여러 몬스터·여러 스킬", text)
    text = re.sub(r"다섯 스킬", "모든 스킬", text)
    text = re.sub(r"다섯 몬스터", "모든 몬스터", text)
    text = re.sub(r"다섯 스킬이 각각 PASS이고", "모든 필수 스킬 역할이 각각 PASS이고", text)
    text = re.sub(r"- VFX \d+장: [^\n]+", f"- VFX {total_vfx}장: {distribution}", text)
    text = re.sub(r"- ICON \d+장", f"- ICON {icon_count}장", text)
    text = text.replace("마노를 버섯처럼 다른 몬스터로 바꾼 이미지\n- ", "다른 몬스터·캐릭터로 정체성을 바꾼 이미지\n- ")
    text = re.sub(r"이 명령은 AREA \d+ 전체 신규 제작까지 수행한다\. AREA 01 이후는 자동 시작하지 않는다\.", f"이 명령은 AREA {area} 전체 신규 제작까지만 수행한다. 다른 Area는 자동 시작하지 않는다.", text)
    text = text.replace("8프레임의 흐름은", "6프레임은 준비/성장/절정/해체/fade를 실제 형상으로 배분한다. 8프레임의 흐름은")
    text = text.replace(
        "- 8프레임: 1024×1024 source sheet 안에 4열×2행의 동일 크기 정사각 셀을 배치한다.",
        "- 6프레임: 1024×1024 source sheet 안에 3열×2행의 동일 크기 정사각 셀을 배치한다.\n- 8프레임: 1024×1024 source sheet 안에 4열×2행의 동일 크기 정사각 셀을 배치한다.",
    )
    text += f"\n\n## 이 Area의 계산된 필수 수량\n\n- Area: `{area}` / {area_name}\n- manifest 스킬: {len(rows)}\n- VFX 필수 스킬: {len(vfx_rows)} / 총 {total_vfx}프레임\n- ICON-only 또는 ICON 포함 전체: {icon_count}개 ICON\n- 패시브 ICON-only는 RUNTIME_ROLE_MAP을 우선하며 VFX를 임의 생성하지 않는다.\n"
    return text, total_vfx, icon_count, anchor["skill_id"]


def make_quality(area, total_vfx, icon_count, anchor):
    return f'''# AREA {area} 제작 품질 게이트

외부 TXT/CHATGPT_IMAGES_MASTER_PROMPT의 단일 스킬 파이프라인을 따른다. 여러 스킬을 한 이미지에 생성하면 즉시 FAIL이다.

## 첫 파이프라인 게이트

`{anchor}`의 필수 VFX가 참조 입력, 원화, 프레임 분리, 알파, 동작, ICON 게이트를 통과하기 전 나머지 스킬을 생성하지 않는다. 실패 원인을 분류하고 방식이나 프롬프트를 바꿔 같은 스킬만 다시 만든다. 같은 방식의 반복 재시도는 금지한다.

## 스킬별 PASS

- Identity: manifest와 GENERATION_SPEC의 WHAT, 소재, 팔레트, 방향 유지
- References: MONSTER_IMAGE와 두 prepared board를 실제 생성 입력으로 사용하고 경로·SHA-256 기록
- VFX: RUNTIME_ROLE_MAP이 요구한 경우 명세 수량의 개별 256×256 RGBA PNG 존재
- Passive: ICON-only는 불필요한 VFX를 만들지 않음
- Motion: RGB 형상이 같고 alpha만 달라지는 방식이 아니며 준비·성장·절정·해체·fade가 실제 형태 변화
- Stability: 같은 pivot/축/공통 스케일이며 프레임별 자동 크롭 흔들림 없음
- Rendering: 어두운 유색 면, 중간톤, 밝은 코어, 재질별 반사와 통제된 파편 구분
- Alpha: 바깥쪽 완전 투명 픽셀과 반투명 가장자리, 흰/검정/회색 matte 없음
- Isolation: 텍스트·번호·UI·몬스터 본체·다른 셀·공식 캐릭터/무기 없음
- Icon: 256×256 RGBA, 64px 읽힘, 완성 VFX 또는 고정 소재와 연결

## Area 패키징 PASS

- 정확히 VFX {total_vfx}장, ICON {icon_count}장
- 연속 번호, 정확한 이름·폴더·canvas·RGBA
- 최종 PNG로 합성한 preview/contact/animation viewer
- manifest/result/validation/reference/state/source·추출 기록
- ZIP CRC와 각 엔트리 SHA-256 확인

하나라도 실패하면 정상 이름 `AREA_{area}_IMAGES_OUTPUT.zip`을 만들지 않는다. 실패 시안과 보고서만 든 ZIP은 납품물이 아니다.
'''


def make_readme(area, area_name, anchor):
    return f'''# AREA {area} {area_name} 이미지 신규 제작 — 여기서 시작

사용자는 이 `AREA_{area}_IMAGES_INPUT.zip`과 `AREA_{area}_CHATGPT_PRODUCTION_PROMPT.txt`만 첨부하고 “첨부한 프롬프트대로 실행해줘”라고 요청한다.

`CHATGPT_IMAGES_MASTER_PROMPT.md`는 외부 TXT와 같은 최종 실행 절차다. `{anchor}` 하나로 참조 입력→VFX source→프레임 추출→알파/동작 검증→ICON 파이프라인을 먼저 통과시킨다. 그 뒤 manifest 순서대로 한 스킬씩 만든다. 여러 스킬을 한 이미지에 동시에 생성하지 않는다.

각 몬스터 폴더의 `DESIGN_REFERENCE_BRIEF.md`에는 소재와 원본 참조가 있고, `reference_resource_design/prepared_boards/`에는 생성 호출에 전달할 스킬별 공식 VFX 보드와 승인 AREA00 마감 보드가 있다. BOARD_MANIFEST.json에 보드 구성 원본·SHA-256·타일 위치를 기록했다.

RUNTIME_ROLE_MAP이 ICON-only로 정한 패시브는 ICON만 제작한다. 기존 OUTPUT은 덮어쓰지 않으며 결과는 REVIEW_CANDIDATE다. 게임 RUID·AnimationClip·scale·offset은 변경하지 않는다. 다른 Area는 자동 시작하지 않는다.
'''


def build_boards(data, rows, mappings):
    by_skill = {m["skill_id"]: m for m in mappings}
    prefix = "reference_resource_design/prepared_boards/"
    data = {p: b for p, b in data.items() if not p.startswith(prefix)}
    reports = []
    for row in rows:
        mapping = by_skill[row["skill_id"]]
        official_paths = balanced_representatives(mapping["elements"], 16)
        official_entries = [{"path": p, "bytes": data[p], "purpose": "official VFX phase reference"} for p in official_paths]
        official_board, official_tiles = contact_board(official_entries)
        finish_paths = list(mapping["area00_full_vfx"])
        if len(finish_paths) > 12:
            indexes = sorted(set(round(i * (len(finish_paths) - 1) / 11) for i in range(12)))
            finish_paths = [finish_paths[i] for i in indexes]
        icon_paths = [e["source_path"] for e in mapping["elements"] if e["role"] == "icon"] + [mapping["area00_icon"]]
        finish_entries = [{"path": p, "bytes": data[p], "purpose": "approved AREA00 finish/motion reference"} for p in finish_paths]
        finish_entries += [{"path": p, "bytes": data[p], "purpose": "official/approved ICON rendering reference"} for p in icon_paths]
        finish_board, finish_tiles = contact_board(finish_entries)
        official_name = prefix + row["skill_id"] + "_OFFICIAL_VFX_BOARD.png"
        finish_name = prefix + row["skill_id"] + "_AREA00_FINISH_BOARD.png"
        manifest_name = prefix + row["skill_id"] + "_BOARD_MANIFEST.json"
        monster = row["folder"] + "/MONSTER_IMAGE.png"
        meta = {
            "skill_id": row["skill_id"], "monster_id": row["monster_id"],
            "monster_image": monster, "monster_image_sha256": sha(data[monster]),
            "official_vfx_board": {"path": official_name, "sha256": sha(official_board), "tiles": official_tiles},
            "area00_finish_board": {"path": finish_name, "sha256": sha(finish_board), "tiles": finish_tiles},
            "required_generation_inputs": [monster, official_name, finish_name],
            "board_background": "neutral gray; reference transport only; never copy into OUTPUT",
        }
        data[official_name] = official_board
        data[finish_name] = finish_board
        data[manifest_name] = json.dumps(meta, ensure_ascii=False, indent=2).encode("utf-8")
        brief_path = row["folder"] + "/DESIGN_REFERENCE_BRIEF.md"
        brief = decode(data[brief_path]).split("## 제작 호출에 바로 사용할 준비 보드")[0].rstrip()
        brief += f'''\n\n## 제작 호출에 바로 사용할 준비 보드\n\n- 실제 몬스터: `{monster}` / SHA-256 `{sha(data[monster])}`\n- 공식 VFX 다단계 보드: `{official_name}` / SHA-256 `{sha(official_board)}`\n- 승인 AREA00 마감·ICON 보드: `{finish_name}` / SHA-256 `{sha(finish_board)}`\n- 구성 원본·타일·해시: `{manifest_name}`\n\n이 세 이미지를 해당 스킬 생성의 실제 reference input으로 전달한다. 회색 바탕·격자·참조 고유 소재는 결과에 넣지 않는다. 여러 스킬을 한 번에 생성하지 않는다.\n'''
        data[brief_path] = brief.encode("utf-8")
        reports.append(meta)
    data[prefix + "README.md"] = (
        "# Prepared reference boards\n\n각 스킬 생성 호출에 전달할 공식 VFX 보드와 승인 AREA00 마감 보드다. "
        "보드는 실제 원본의 전달용 합성물이며 출력물이 아니다. BOARD_MANIFEST.json에 원본 경로·SHA-256·타일 위치가 있다.\n"
    ).encode("utf-8")
    return data, reports


def write_hash_index(data):
    records = [{"path": p, "sha256": sha(b), "bytes": len(b)} for p, b in sorted(data.items()) if p != "INPUT_FILE_HASHES.csv"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["path", "sha256", "bytes"], lineterminator="\n")
    writer.writeheader(); writer.writerows(records)
    data["INPUT_FILE_HASHES.csv"] = stream.getvalue().encode("utf-8-sig")
    return records


def main():
    packages = sorted(BASE.glob("AREA_*_IMAGES_INPUT.zip"))
    prompts = sorted(BASE.glob("AREA_*_CHATGPT_PRODUCTION_PROMPT.txt"))
    assert len(packages) == len(prompts) == 20
    template = (BASE / "AREA_00_CHATGPT_PRODUCTION_PROMPT.txt").read_text(encoding="utf-8-sig")
    backup = COLLECTION / "backups" / f"INPUTS_BEFORE_COMMAND_REBUILD_ALL_{STAMP}.zip"
    backup.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(backup, "x", zipfile.ZIP_STORED) as out:
        for path in packages + prompts + [BASE / "ALL_AREAS_INDEX.csv", BASE / "ALL_AREAS_INDEX.md"]:
            out.write(path, path.name)
    report = {"status": "PASS", "timestamp": STAMP, "backup": str(backup), "areas": []}
    for zip_path in packages:
        area = zip_path.stem[5:7]
        root = zip_path.stem + "/"
        with zipfile.ZipFile(zip_path) as archive:
            data = {n[len(root):]: archive.read(n) for n in archive.namelist() if n.startswith(root) and not n.endswith("/")}
        rows = list(csv.DictReader(io.StringIO(decode(data["AREA_MANIFEST.csv"]))))
        area_name = rows[0]["area_name"]
        specs = {r["skill_id"]: parse_skill_spec(data, r["folder"]) for r in rows}
        roles = {r["skill_id"]: runtime_roles(data, r["folder"]) for r in rows}
        mappings = json.loads(data["reference_resource_design/AREA_REFERENCE_MAP.json"])
        assert {r["skill_id"] for r in rows} == {m["skill_id"] for m in mappings}
        data, boards = build_boards(data, rows, mappings)
        prompt, total_vfx, icon_count, anchor = make_prompt(area, area_name, rows, specs, roles, template)
        prompt_bytes = prompt.encode("utf-8")
        data["CHATGPT_IMAGES_MASTER_PROMPT.md"] = prompt_bytes
        data["README_START_HERE.md"] = make_readme(area, area_name, anchor).encode("utf-8")
        data["QUALITY_GATE.md"] = make_quality(area, total_vfx, icon_count, anchor).encode("utf-8")
        data["COMMAND_SYSTEM_VERSION.json"] = json.dumps({
            "area": area, "area_name": area_name, "version": "single-skill-pipeline-v1",
            "rebuilt_at": STAMP, "skills": len(rows), "required_vfx_frames": total_vfx,
            "required_icons": icon_count, "prepared_boards": len(boards) * 2,
            "area_wide_generation": "FORBIDDEN", "anchor_skill": anchor,
            "external_prompt_equals_internal_master": True,
            "previous_outputs_are_positive_references": False,
        }, ensure_ascii=False, indent=2).encode("utf-8")
        hash_records = write_hash_index(data)
        temp = zip_path.with_suffix(".zip.tmp")
        with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as out:
            for path, blob in sorted(data.items()): out.writestr(root + path, blob)
        with zipfile.ZipFile(temp) as check:
            assert check.testzip() is None
            assert check.read(root + "CHATGPT_IMAGES_MASTER_PROMPT.md") == prompt_bytes
            assert sum(n.endswith("_BOARD.png") for n in check.namelist()) == len(rows) * 2
            assert sum(n.endswith("_BOARD_MANIFEST.json") for n in check.namelist()) == len(rows)
            for board in boards:
                for path in board["required_generation_inputs"]: assert root + path in check.namelist()
                for group in (board["official_vfx_board"], board["area00_finish_board"]):
                    assert sha(check.read(root + group["path"])) == group["sha256"]
                    for tile in group["tiles"]: assert sha(check.read(root + tile["source_path"])) == tile["source_sha256"]
            for record in hash_records: assert sha(check.read(root + record["path"])) == record["sha256"]
        temp.replace(zip_path)
        txt_path = BASE / f"AREA_{area}_CHATGPT_PRODUCTION_PROMPT.txt"
        txt_path.write_bytes(prompt_bytes)
        item = {"area": area, "area_name": area_name, "skills": len(rows), "vfx_frames": total_vfx,
                "icons": icon_count, "prepared_boards": len(boards) * 2, "anchor": anchor,
                "zip_bytes": zip_path.stat().st_size, "zip_sha256": sha(zip_path.read_bytes()),
                "prompt_sha256": sha(prompt_bytes), "status": "PASS"}
        report["areas"].append(item)
        print(json.dumps(item, ensure_ascii=False), flush=True)
    index_path = BASE / "ALL_AREAS_INDEX.csv"
    index = list(csv.DictReader(io.StringIO(index_path.read_text(encoding="utf-8-sig"))))
    for row in index:
        item = next(x for x in report["areas"] if x["area"] == row["area_num"].zfill(2))
        row.update(zip_bytes=item["zip_bytes"], zip_sha256=item["zip_sha256"], prompt_sha256=item["prompt_sha256"])
    stream = io.StringIO(newline=""); writer = csv.DictWriter(stream, fieldnames=list(index[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(index)
    index_temp = index_path.with_suffix(".csv.tmp")
    index_temp.write_bytes(b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8"))
    index_temp.replace(index_path)
    overview = ["# AREA 00–20 단일 스킬 제작 패키지", "", "각 Area의 ZIP과 TXT 두 파일만 함께 첨부한다. AREA06은 운영 목록에 없어 만들지 않았다.", ""]
    for row in index:
        overview.append(f'- AREA {row["area_num"]}: [{row["zip_file"]}]({row["zip_file"]}) + [{row["prompt_file"]}]({row["prompt_file"]})')
    (BASE / "ALL_AREAS_INDEX.md").write_text("\n".join(overview) + "\n", encoding="utf-8")
    report["total_areas"] = len(report["areas"]); report["total_skills"] = sum(x["skills"] for x in report["areas"])
    report["total_vfx_frames"] = sum(x["vfx_frames"] for x in report["areas"])
    report["total_icons"] = sum(x["icons"] for x in report["areas"])
    report["total_prepared_boards"] = sum(x["prepared_boards"] for x in report["areas"])
    report["checks"] = ["20 ZIP CRC", "104 per-skill three-image input paths", "208 prepared board hashes and source tiles",
                        "RUNTIME_ROLE_MAP-aware VFX/icon counts", "external TXT equals internal master", "all input entry hashes", "index hashes"]
    (COLLECTION / "ALL_AREA_COMMAND_SYSTEM_VALIDATION.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("COMPLETE", report["total_areas"], report["total_skills"], report["total_vfx_frames"], report["total_icons"], report["total_prepared_boards"], flush=True)


if __name__ == "__main__": main()
