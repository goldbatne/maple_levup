from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import time
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "docs" / "art"
INPUTS = ART / "images-input-packages"
ARCHIVES = ART / "images-input-packages_archive"
REF_CACHE = ART / "current-skill-reference-cache"
AREA00_RUN = ART / "area00_refinement" / "20260912_203404"
AREA00_ZIP = AREA00_RUN / "AREA_00_IMAGES_OUTPUT_REFINED_CANDIDATE.zip"
AREA00_STYLE = AREA00_RUN / "STYLE_BASELINE_CANDIDATE.md"
AREA00_OVERVIEW = AREA00_RUN / "AREA_OVERVIEW_PREVIEW.png"

RESOURCE_SEARCH_URL = "https://maplestoryworlds-resourcesearch-new.nexon.com/search?category=skill"
API_BASE = "https://maplestoryworlds-resourcesearch-new.nexon.com/api"
CDN_BASE = "https://mod-resource-search-images.dn.nexoncdn.co.kr/maplestory_world"

# Every entry below was resolved through the official MSW resource search API.
# A result is treated as name-verified only when the Korean name of the returned
# first pack exactly matched the query. Dates are chronology evidence for the
# skill/update, not an unprovable per-file asset revision timestamp.
REFERENCES = [
    {
        "key": "sol_janus_dawn",
        "name": "솔 야누스 : 새벽",
        "pack_id": "skill/50000.img/skill/500001003",
        "chronology": "2023-12-21 공용 6차 코어 추가",
        "official_url": "https://maplestory.nexon.com/news/update/731",
        "status": "CURRENT_NAMED_REFERENCE",
        "families": "persistent|summon|field|aura",
        "effect_ruid": "42556f51b9a542678b98d225e665b836",
        "icon_ruid": "c0af00f1a35b496582932d23471a6403",
        "elements": [
            ["animationclip", "42556f51b9a542678b98d225e665b836", "effect"],
            ["sprite", "c0af00f1a35b496582932d23471a6403", "icon"],
            ["sprite", "df8a7d5269784e849c92d15ee5188a9d", "iconDisabled"],
            ["sprite", "05f893097ff74e1d8debb7c836af6f88", "iconMouseOver"],
            ["animationclip", "306345a6c275492b95777d482e2ca393", "special"],
            ["animationclip", "dfe9750daa914bc7a32536b58433ca62", "hit/0"],
            ["animationclip", "5a279d3b2dc4401cba005ce00f20fb3a", "summon/die"],
            ["animationclip", "15778a3982df41ae9a73d05ee779edf0", "summon/stand"],
            ["animationclip", "4956b1cf7e2e465ebaa4a036de57300d", "summon/summoned"],
        ],
    },
    {
        "key": "sol_janus_dusk",
        "name": "솔 야누스 : 황혼",
        "pack_id": "skill/50000.img/skill/500001001",
        "chronology": "2023-12-21 공용 6차 코어 추가",
        "official_url": "https://maplestory.nexon.com/news/update/731",
        "status": "CURRENT_NAMED_REFERENCE",
        "families": "persistent|multi-hit|falling|field",
        "effect_ruid": "569dae6ccfea4a558fb5d2d0b7cf263d",
        "icon_ruid": "44dcf8431e9d485a99f4127ae51a3703",
        "elements": [
            ["animationclip", "569dae6ccfea4a558fb5d2d0b7cf263d", "effect"],
            ["sprite", "44dcf8431e9d485a99f4127ae51a3703", "icon"],
            ["sprite", "6e837adb6d4b42c29660de4d431b96a0", "iconDisabled"],
            ["sprite", "53bce7bb86fe4fc2b3c7d3d08e43819d", "iconMouseOver"],
            ["animationclip", "bc2fc9ebec4c488197142217d0d2d549", "hit/0"],
            ["animationclip", "369c93d774524b8db32d6c9f4fb814be", "hit/1"],
            ["animationclip", "0f0f0028769b44f3b7d0e9a79eeb6048", "hit/2"],
            ["animationclip", "8f47f30b605740b3aadccb599b403f1f", "hit/3"],
            ["animationclip", "91215cc2e6c249149ced257df2a3006c", "hit/4"],
        ],
    },
    {
        "key": "hex_sandstorm",
        "name": "헥스 : 샌드스톰",
        "pack_id": "skill/15414.img/skill/154141500",
        "chronology": "6차 스킬 계열; 공식 리소스 팩 이름 일치",
        "official_url": "https://maplestory.nexon.com/news/update/712",
        "status": "NAMED_STRUCTURE_REFERENCE",
        "families": "charge|area|earth|wind|impact",
        "effect_ruid": "28c33a05afb04953a8b3527b9a374382",
        "icon_ruid": "7e6eda520af54b87bc552712f3804ea6",
        "elements": [
            ["sprite", "7e6eda520af54b87bc552712f3804ea6", "icon"],
            ["sprite", "2122b97884be470d9258690bf6a49a1d", "iconDisabled"],
            ["sprite", "21220e46c6454fc5be71ce5b6025448d", "iconMouseOver"],
            ["animationclip", "28c33a05afb04953a8b3527b9a374382", "keydown"],
            ["animationclip", "b97b5eda839440c3921f38656ef77649", "keydownend"],
            ["animationclip", "68f99c9a1c9844908757d29d8b84ec9f", "prepare"],
            ["animationclip", "6b28eb427ab9412fbe23e321b71dd64a", "prepare0"],
            ["animationclip", "8d621cb939c34cfb97d2f73a8e0f4e5c", "hit/0"],
        ],
    },
    {
        "key": "dark_synthesis_vi",
        "name": "다크 신서시스 VI",
        "pack_id": "skill/134.img/skill/1341003",
        "chronology": "2023-12-28 6차 마스터리 코어 추가",
        "official_url": "https://maplestory.nexon.com/testworld/news/update/17",
        "status": "NAMED_STRUCTURE_REFERENCE",
        "families": "dark|area|wave|explosion",
        "effect_ruid": "dc04344c2a814f188b0795ba5e445319",
        "icon_ruid": "ca7e6cfa37464ab8bb780817e479ca6a",
        "elements": [
            ["animationclip", "dc04344c2a814f188b0795ba5e445319", "effect"],
            ["sprite", "ca7e6cfa37464ab8bb780817e479ca6a", "icon"],
            ["sprite", "14bb706327454c83bc5c4e291ae15a27", "iconDisabled"],
            ["sprite", "e3a2adfd36d0446e9ef76b81ba634a05", "iconMouseOver"],
            ["animationclip", "5a3b6db42a3e4e2e8b1428de9a3de764", "hit/0"],
        ],
    },
    {
        "key": "assassinate_vi",
        "name": "암살 VI",
        "pack_id": "skill/424.img/skill/4241001",
        "chronology": "6차 스킬 계열; 공식 리소스 팩 이름 일치",
        "official_url": "https://maplestory.nexon.com/news/update/712",
        "status": "NAMED_STRUCTURE_REFERENCE",
        "families": "melee|dash|sharp|impact|multi-stage",
        "effect_ruid": "5be8668a22e34a84bc218ee96c40ab19",
        "icon_ruid": "a8ef90fb53da4ab0b30ee662a96198b8",
        "elements": [
            ["animationclip", "5be8668a22e34a84bc218ee96c40ab19", "effect"],
            ["animationclip", "83891a6b78fb4861a3d6e53a51306ec9", "effect2"],
            ["sprite", "a8ef90fb53da4ab0b30ee662a96198b8", "icon"],
            ["sprite", "19cf34fbd64e4c4c8692896556e0e850", "iconDisabled"],
            ["sprite", "6e6d38b06da1451893e31e04ed3971e8", "iconMouseOver"],
            ["animationclip", "888e0446d74b40728451e5edc1c6714d", "hit/0"],
            ["animationclip", "ce5b90adf98241ca86e6bb48b7c41a42", "hit2/0"],
        ],
    },
    {
        "key": "light_of_courage",
        "name": "라이트 오브 커리지",
        "pack_id": "skill/40001.img/skill/400011127",
        "chronology": "공식 리소스 팩 이름 일치; 자산 개정일 미제공",
        "official_url": "https://maplestoryworlds-resourcesearch-new.nexon.com/search?category=skill&selected=skill/40001.img/skill/400011127",
        "status": "SUPPLEMENTARY_STRUCTURE_REFERENCE",
        "families": "buff|shield|aura|loop|end",
        "effect_ruid": "47d02b9a7fd54d418e76cd633f8b5768",
        "icon_ruid": "ab8d8a7b108a4df185353df5d992a828",
        "elements": [
            ["animationclip", "d0c52ee3fd464c8fa94edfd6fa7bde42", "affected"],
            ["animationclip", "0029ad5c787e4302894c687ee9fda8dd", "affected0"],
            ["animationclip", "47d02b9a7fd54d418e76cd633f8b5768", "effect"],
            ["animationclip", "778b52a102f14c168b5097544e3fc011", "end"],
            ["sprite", "ab8d8a7b108a4df185353df5d992a828", "icon"],
            ["animationclip", "b5c8dfbb5e114d29bfebddb1735ac385", "repeat"],
            ["animationclip", "06e57cc1f3144b41a51ccf90480a6d14", "special"],
        ],
    },
]

CURRENTNESS_EXCLUSIONS = [
    {
        "name": "얼티메이트-싸이킥 샷 VI",
        "pack_id": "skill/14214.img/skill/142140004",
        "reason": "2025-12-18 키네시스 리마스터에서 삭제 확인. 팩 구조는 조회되지만 현행 positive visual reference에서 제외.",
        "official_url": "https://maplestory.nexon.com/news/update/792",
    }
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def download(url: str, target: Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "Codex MSW input package builder"})
    with urllib.request.urlopen(request, timeout=30) as response:
        target.write_bytes(response.read())


def image_record(path: Path) -> dict:
    with Image.open(path) as im:
        frames = getattr(im, "n_frames", 1)
        im.seek(0)
        rgba = im.convert("RGBA")
        alpha = rgba.getchannel("A")
        return {
            "file": path.name,
            "format": im.format,
            "width": rgba.width,
            "height": rgba.height,
            "frames": frames,
            "alpha_min": alpha.getextrema()[0],
            "alpha_max": alpha.getextrema()[1],
            "sha256": sha256_file(path),
        }


def build_reference_cache() -> list[dict]:
    if REF_CACHE.exists():
        shutil.rmtree(REF_CACHE)
    REF_CACHE.mkdir(parents=True)
    records = []
    for i, ref in enumerate(REFERENCES, 1):
        folder = REF_CACHE / f"{i:02d}_{ref['key']}"
        folder.mkdir(parents=True)
        animation = folder / "animation_preview.gif"
        icon = folder / "icon_preview.png"
        download(f"{CDN_BASE}/{ref['effect_ruid']}.gif", animation)
        download(f"{CDN_BASE}/{ref['icon_ruid']}.png", icon)
        animation_info = image_record(animation)
        icon_info = image_record(icon)
        record = {
            "order": i,
            "key": ref["key"],
            "skill_name": ref["name"],
            "pack_id": ref["pack_id"],
            "status": ref["status"],
            "chronology_evidence": ref["chronology"],
            "official_url": ref["official_url"],
            "families": ref["families"],
            "effect_ruid": ref["effect_ruid"],
            "icon_ruid": ref["icon_ruid"],
            "animation_frames": animation_info["frames"],
            "animation_size": f"{animation_info['width']}x{animation_info['height']}",
            "animation_sha256": animation_info["sha256"],
            "icon_size": f"{icon_info['width']}x{icon_info['height']}",
            "icon_sha256": icon_info["sha256"],
        }
        records.append(record)
        structure = "\n".join(
            f"| {kind} | `{ruid}` | `{rel}` |" for kind, ruid, rel in ref["elements"]
        )
        write_text(
            folder / "info.md",
            f"""# {ref['name']}

- 공식 MSW resource pack: `{ref['pack_id']}`
- 분류: `{ref['status']}`
- 시기 근거: {ref['chronology']}
- 시기 근거 URL: {ref['official_url']}
- 적용 계열: `{ref['families']}`
- 대표 animationclip RUID: `{ref['effect_ruid']}`
- 대표 icon RUID: `{ref['icon_ruid']}`
- 조회 방식: MSW 공식 리소스 검색기와 `/api/v3/search/resources` 결과에서 첫 한국어 이름이 질의와 일치함을 확인

## 팩 역할 구조

| type | RUID | rel_path |
|---|---|---|
{structure}

## 사용 제한

이 자료는 레이어 분리, 프레임 리듬, 외곽-중간톤-코어의 렌더링 문법, ICON/VFX 연결을 관찰하는 참고다. 캐릭터, 무기, 고유 문양, 고유 실루엣, 공격 메커니즘은 복제하지 않는다.
""",
        )
        write_text(folder / "ruid.txt", ref["effect_ruid"] + "\n" + ref["icon_ruid"])

    columns = list(records[0].keys())
    write_csv(REF_CACHE / "STYLE_INDEX.csv", records, columns)
    table = "\n".join(
        "| " + " | ".join(str(row[c]).replace("|", "\\|") for c in columns) + " |"
        for row in records
    )
    write_text(
        REF_CACHE / "STYLE_INDEX.md",
        "# Curated MSW Skill Reference Index\n\n"
        "검색 순위가 아니라 정확한 팩 이름과 공식 시기 근거를 함께 기록한 축소 코퍼스다. "
        "MSW API는 자산 개정일을 제공하지 않으므로 스킬 추가일과 파일 개정일을 같은 것으로 쓰지 않는다.\n\n"
        "| " + " | ".join(columns) + " |\n| " + " | ".join("---" for _ in columns) + " |\n" + table,
    )
    write_text(
        REF_CACHE / "summary" / "STYLE_ATLAS.md",
        """# AREA 00 + MSW resource pack 관찰 기준

## 우선순위

1. 각 몬스터의 WHAT은 `AREA_MANIFEST`, `MONSTER_INFO`, `GENERATION_SPEC`, `RUNTIME_ROLE_MAP`으로 고정한다.
2. 마감 품질은 `area00_finish_baseline`의 실제 최종 PNG에서 읽는다.
3. 역할 분리와 시간 구조는 `CURRENT_NAMED_REFERENCE`와 `NAMED_STRUCTURE_REFERENCE`의 실제 팩 구성에서 읽는다.
4. `SUPPLEMENTARY_STRUCTURE_REFERENCE`는 해당 역할이 필요할 때만 쓴다.
5. `CURRENTNESS_EXCLUSIONS.md`에 있는 팩은 시각 자료를 포함하지 않으며 positive reference로 사용하지 않는다.

## 관찰할 렌더링 문법

- 어두운 유색 외곽 또는 밀도 높은 그림자가 전체 실루엣을 잡는다.
- 고유 재질을 설명하는 중간톤 면이 있고, 밝은 코어와 하이라이트가 그 위에 제한적으로 올라간다.
- bloom은 코어를 삼키지 않으며, 가장자리 알파가 갑자기 끊기거나 흰 테두리로 굳지 않는다.
- 파편은 크기와 방향에 위계가 있고, 절정 뒤에는 감속·분해·fade로 사라진다.
- 모든 프레임을 같은 광량으로 채우지 않는다. 준비→성장→절정→해체→fade가 형태 변화로 읽혀야 한다.
- 포스터 배경, 캐릭터 전신, 장면 조명, UI 프레임 없이 단독 게임 VFX 자산으로 읽혀야 한다.

## ICON

- 기본 납품은 256x256 RGBA 1장이다. 런타임 명세가 요구하지 않는 disabled/mouseover 상태는 만들지 않는다.
- VFX의 핵심 명사 하나와 보조 움직임 하나를 같은 색·재질 언어로 압축한다.
- 64px 축소에서도 외곽과 코어가 분리되어야 한다.
""",
    )
    exclusion_lines = "\n".join(
        f"- **{item['name']}** `{item['pack_id']}`: {item['reason']} 근거: {item['official_url']}"
        for item in CURRENTNESS_EXCLUSIONS
    )
    write_text(
        REF_CACHE / "CURRENTNESS_EXCLUSIONS.md",
        "# Currentness exclusions\n\n검색 결과에는 남아 있지만 현행 제작의 positive visual reference에서 제외한 항목이다. 이미지 파일은 패키지에 넣지 않는다.\n\n" + exclusion_lines,
    )
    snapshot = {
        "captured_at": datetime.now().astimezone().isoformat(),
        "resource_search_url": RESOURCE_SEARCH_URL,
        "api_base": API_BASE,
        "method": "official website plus official REST API wrapper; exact Korean first-result name checked",
        "asset_revision_date_available": False,
        "references": REFERENCES,
        "currentness_exclusions": CURRENTNESS_EXCLUSIONS,
    }
    write_text(REF_CACHE / "RESOURCE_API_SNAPSHOT.json", json.dumps(snapshot, ensure_ascii=False, indent=2))
    return records


def build_area00_baseline(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AREA00_STYLE, target / "STYLE_BASELINE_CANDIDATE.md")
    shutil.copy2(AREA00_OVERVIEW, target / "AREA_OVERVIEW_PREVIEW.png")
    with zipfile.ZipFile(AREA00_ZIP) as z:
        names = z.namelist()
        for name in names:
            if "/ICON/" in name and name.endswith(".png"):
                out = target / "icons" / Path(name).name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(z.read(name))
        groups: dict[str, list[str]] = {}
        for name in names:
            if "/VFX/" not in name or not name.endswith(".png"):
                continue
            monster = name.split("/monsters/", 1)[1].split("/", 1)[0]
            groups.setdefault(monster, []).append(name)
        for monster, frames in groups.items():
            frames.sort()
            picks = sorted({0, max(0, len(frames) // 2), len(frames) - 1})
            for idx in picks:
                name = frames[idx]
                out = target / "selected_vfx_frames" / monster / Path(name).name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(z.read(name))
    write_text(
        target / "README.md",
        """# AREA 00 finish baseline

이 폴더는 실제 AREA 00 수정 후보의 최종 PNG에서 추출한 마감 기준이다.

- 참고: 명암 구조, 재질의 층, 밝은 코어, 반투명 가장자리, 프레임 간 형태 변화, ICON/VFX 연결
- 복제 금지: AREA 00의 저레벨 크기, 색상, 방울·껍질·무지개 형상, 프레임 수, 스킬 구성
- `selected_vfx_frames`는 각 스킬의 시작/중간/끝 대표 프레임이며 전체 애니메이션을 대체하지 않는다.
- 원본: `docs/art/area00_refinement/20260912_203404/AREA_00_IMAGES_OUTPUT_REFINED_CANDIDATE.zip`
""",
    )


def parse_manifest(root: Path) -> list[dict]:
    with (root / "AREA_MANIFEST.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def choose_refs(row: dict, spec: str) -> tuple[list[str], str]:
    text = " ".join([row.get("skill_name", ""), row.get("skill_type", ""), row.get("actual_effect", ""), spec])
    if row.get("skill_type") in {"패시브", "버프"} or any(k in text for k in ["보호", "장막", "피부", "껍질", "갑주", "회복"]):
        return ["light_of_courage", "sol_janus_dawn"], "닫힌 버프/아이콘 실루엣과 effect-repeat-end 역할 분리"
    if any(k in text for k in ["돌진", "베기", "할퀴", "찌르", "물어", "박치기"]):
        return ["assassinate_vi", "dark_synthesis_vi"], "진행 방향이 선명한 주형과 별도 hit 절정"
    if any(k in text for k in ["모래", "폭풍", "지진", "암석", "돌", "뿌리", "포자", "분진"]):
        return ["hex_sandstorm", "dark_synthesis_vi"], "준비-키다운-종료 구조와 범위 절정/파편 해체"
    if any(k in text for k in ["탄", "구슬", "광선", "발사", "투척", "숨결"]):
        return ["assassinate_vi", "sol_janus_dusk"], "본체/타격 역할 분리와 반복 피격 변주"
    if any(k in text for k in ["소환", "영역", "장판", "시간", "고리", "별", "달", "태양"]):
        return ["sol_janus_dawn", "sol_janus_dusk"], "지속형 본체와 다중 hit/소멸 역할 분리"
    return ["dark_synthesis_vi", "sol_janus_dusk"], "단일 effect와 별도 hit, 절정 이후 단계적 fade"


def append_assignment(spec_path: Path, row: dict) -> None:
    original = spec_path.read_text(encoding="utf-8-sig").rstrip()
    keys, reason = choose_refs(row, original)
    refs = {r["key"]: r for r in REFERENCES}
    lines = []
    for key in keys:
        ref = refs[key]
        lines.append(f"- `{key}` / {ref['name']}: {ref['families']} — {reason}")
    block = f"""

## 이번 개편의 지정 레퍼런스

{chr(10).join(lines)}
- 마감 기준: `global_skill_style_library/area00_finish_baseline/`의 실제 AREA 00 최종 PNG
- 적용 범위: 명암 구조, 재질 층, 코어광, 알파 가장자리, 프레임 리듬, ICON/VFX 연결
- 금지: 레퍼런스의 캐릭터·무기·고유 문양·고유 실루엣·팔레트·공격 메커니즘 복제
- 기존 AREA 01~20 OUTPUT과 실패 샘플은 positive reference로 사용하지 않는다.
"""
    if "## 이번 개편의 지정 레퍼런스" in original:
        original = original.split("## 이번 개편의 지정 레퍼런스", 1)[0].rstrip()
    write_text(spec_path, original + block)


def ensure_runtime_and_provenance(folder: Path, row: dict, source_zip: Path, source_hash: str, run_id: str) -> None:
    skill_type = row.get("skill_type", "")
    motion = row.get("actual_motion", "")
    if skill_type == "패시브":
        required_roles = "ICON"
        vfx_note = "현행 패키지 선언상 런타임 VFX 없음. 패시브는 기본 ICON만 필수 NEW_ART다."
    else:
        required_roles = "ICON | VFX"
        vfx_note = "GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다."
    projectile_note = ""
    if "투사체" in motion or "projectile" in motion.lower():
        required_roles += " | PROJECTILE_READING"
        projectile_note = "\n- PROJECTILE_READING은 투사체 진행 방향과 충돌점 읽힘을 VFX 프레임 안에서 보존한다. 별도 파일은 GENERATION_SPEC가 명시할 때만 만든다."
    write_text(
        folder / "RUNTIME_ROLE_MAP.md",
        f"""# Runtime role map — {row.get('monster_name')} / {row.get('skill_name')}

- monster_id: `{row.get('monster_id')}`
- skill_id: `{row.get('skill_id')}`
- skill_type: `{skill_type}`
- required NEW_ART roles: **{required_roles}**
- declared current motion: {motion}
- role decision: {vfx_note}{projectile_note}
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
""",
    )
    write_text(
        folder / "SOURCE_PROVENANCE.md",
        f"""# Source provenance — {row.get('monster_name')} / {row.get('skill_name')}

- rebuild run: `{run_id}`
- base package: `{source_zip.name}`
- base package SHA-256: `{source_hash}`
- preserved manifest monster image RUID: `{row.get('monster_image_ruid')}`
- preserved monster image status: `{row.get('monster_image_status')}`
- preserved ids: `{row.get('monster_id')}` / `{row.get('skill_id')}`
- preserved WHAT: `{row.get('skill_name')}` / `{row.get('skill_type')}` / `{row.get('actual_effect')}` / `{row.get('actual_motion')}`
- MONSTER_IMAGE.png was copied byte-for-byte from the base canonical package.
- current game data files were not edited or asserted as Maker-registered by this rebuild.
- style references were added from the official MSW resource search website/API and the actual AREA 00 refined candidate; they do not replace the preserved WHAT.
""",
    )


def master_prompt(area_num: str, area_name: str, rows: list[dict]) -> str:
    active = sum(r.get("skill_type") != "패시브" for r in rows)
    passive = len(rows) - active
    return f"""# ChatGPT Images production prompt — AREA {area_num} {area_name}

첨부한 `AREA_{area_num}_IMAGES_INPUT.zip`을 작업 원본으로 사용해 이 Area의 전체 스킬 VFX와 스킬 버튼 ICON을 실제 제작하세요. 검수 보고서만 작성하지 말고 최종 PNG와 OUTPUT ZIP까지 제공하세요.

## 1. 먼저 읽을 파일

1. `README_START_HERE.md`
2. `AREA_MANIFEST.md`와 `.csv`
3. 모든 `monsters/*/MONSTER_INFO.md`, `GENERATION_SPEC.md`, `RUNTIME_ROLE_MAP.md`, `SOURCE_PROVENANCE.md`
4. `global_skill_style_library/summary/STYLE_ATLAS.md`와 `STYLE_INDEX.md`
5. `global_skill_style_library/area00_finish_baseline/`의 실제 PNG
6. `OUTPUT_NAMING_SPEC.md`, `OUTPUT_FORMAT_SPEC.md`, `QUALITY_GATE.md`

이 Area는 몬스터 {len(rows)}종이며 액티브/버프 {active}종, 패시브 {passive}종입니다. manifest의 수량과 다르면 생성을 시작하지 말고 첨부 누락을 먼저 확인하세요.

## 2. 고정할 WHAT

- monster_id, skill_id, 몬스터명, 스킬명, 타입, 실제 효과·동작, 보스 여부를 바꾸지 마세요.
- MONSTER_IMAGE는 해당 몬스터의 색·재질·부위 모티브를 이해하는 입력입니다. 몬스터 본체나 얼굴을 VFX와 ICON에 직접 넣지 마세요.
- 기존 AREA 01~20 OUTPUT, 이전 실패 샘플, 기존 스킬 아이콘은 positive reference가 아닙니다.
- 몬스터마다 중간 승인을 요구하지 마세요. 판단이 필요한 내용은 WHAT을 보존한 상태로 RESULT_INFO에 기록하세요.

## 3. 스타일 레퍼런스의 역할

- AREA 00 최종 PNG에서는 마감 품질만 가져옵니다: 어두운 유색 외곽/그림자, 분명한 중간톤 면, 제한된 밝은 코어, 입체적 재질, 깨끗한 반투명 알파, ICON과 VFX의 공통 형태 언어.
- MSW resource pack에서는 역할 분리와 시간 구조만 가져옵니다: effect와 hit 분리, prepare/hold/end, repeat/end, 다중 hit 변주.
- AREA 00의 저레벨 크기·팔레트·방울·껍질·무지개 모양을 복제하지 마세요.
- 공식 스킬의 캐릭터, 무기, 고유 문양, 고유 실루엣, 공격 메커니즘을 복제하지 마세요.
- `CURRENTNESS_EXCLUSIONS.md`에 기록된 팩은 최신성 오판을 막기 위한 텍스트 기록이며 positive reference로 사용하지 마세요.

## 4. 제작 규칙

- 결과는 포스터·키비주얼·UI 일러스트가 아니라 투명 캔버스에 놓이는 실제 2D 게임 VFX 자산이어야 합니다.
- 각 GENERATION_SPEC의 출력 프로필, 프레임 수, 캔버스, 타이밍을 그대로 따르세요.
- 프레임마다 같은 canvas, pivot, 기준축, 스케일을 유지하고 개별 자동 중앙정렬·자동 크롭을 하지 마세요.
- 준비→성장→절정→해체→fade가 실제 형상 변화로 읽혀야 합니다. 모든 프레임을 같은 광량과 같은 크기의 정지 일러스트로 만들지 마세요.
- 외곽 파편과 발광을 85% 안전영역 안에 두고, 주요 형상은 70% 안에서 읽히게 하세요.
- alpha는 실제 투명/반투명 픽셀을 포함해야 합니다. 흰색·검정색·체커보드·회색 matte, 흰 테두리, 사각형 배경을 넣지 마세요.
- 텍스트, 숫자, UI 프레임, 워터마크, 몬스터 본체를 넣지 마세요.
- ICON은 VFX의 핵심 모티브를 256x256 RGBA 한 장으로 압축하고 64px에서도 읽히게 하세요. 기본 ICON만 필수이며 INPUT이 요구하지 않는 disabled/mouseover 상태를 추가하지 마세요.

## 5. 자체 품질 게이트

각 스킬별로 아래 일곱 항목을 모두 통과한 뒤 다음 스킬로 진행하세요.

1. INPUT의 몬스터·스킬명·타입·효과·역할과 일치한다.
2. 범용 추상 이펙트가 아니라 해당 몬스터 스킬의 소재로 읽힌다.
3. 어두운 외곽→중간톤→밝은 코어의 층과 입체 재질이 있다.
4. 준비→성장→절정→해체→fade 리듬이 자연스럽다.
5. ICON이 VFX와 같은 색·형태·재질 언어를 공유한다.
6. 포스터형 구성, 평면 덩어리, 과한 단일 외곽광, 배경 matte가 없다.
7. 다른 Area/몬스터/공식 스킬의 고유 소재가 섞이지 않았다.

하나라도 실패하면 PASS로 기록하지 말고 그 스킬만 새로 생성하세요. 반복 재시도 횟수로 해결하지 말고 실패 항목에 맞춰 구도·재질·프레임 리듬 지시를 고친 뒤 다시 생성하세요.

## 6. 검증과 납품

- 실제 최종 PNG를 흰색·검정색·중간 회색 배경에 합성해 알파 가장자리를 확인하세요.
- 프레임 수·번호·크기·RGBA·alpha·중심축·안전영역을 기계적으로 검사하세요.
- Area 전체 preview와 labeled preview를 최종 PNG로 합성하세요.
- `OUTPUT_MANIFEST.csv/.md`와 몬스터별 `RESULT_INFO.md`에 생성 도구를 정확히 `native image generation/editing — version/model unverified`로 기록하세요.
- `AREA_{area_num}_IMAGES_OUTPUT/` 구조를 만들고 `AREA_{area_num}_IMAGES_OUTPUT.zip`으로 반환하세요.
- ZIP 안에는 모든 최종 개별 프레임, 모든 기본 ICON, preview, labeled preview, manifest, RESULT_INFO, validation report가 있어야 합니다.
- 파일명·스크린샷·보고서만으로 납품을 대신하지 마세요.
"""


def output_naming(area_num: str) -> str:
    return f"""# Output Naming Spec — AREA {area_num}

출력 루트: `AREA_{area_num}_IMAGES_OUTPUT/`

- VFX: `NNN_[monster_id]_[skill_id]_F00.png`, `F01.png` ...
- ICON: `NNN_[monster_id]_[skill_id]_ICON.png`
- Preview: `NNN_[monster_id]_[skill_id]_CONTACT_PREVIEW.png` 및 `labeled_preview.png`
- NNN은 AREA_MANIFEST의 작업 순번 3자리다.
- monster_id와 skill_id는 축약·번역하지 않는다.
- `F00`부터 마지막 프레임까지 번호를 건너뛰지 않는다.

```text
AREA_{area_num}_IMAGES_OUTPUT/
├─ AREA_OVERVIEW_PREVIEW.png
├─ AREA_OVERVIEW_LABELED_PREVIEW.png
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
├─ VALIDATION_REPORT.md
└─ monsters/
   └─ NNN_[monster_id]_[name]/
      ├─ VFX/*.png
      ├─ ICON/*_ICON.png
      ├─ PREVIEW/*_CONTACT_PREVIEW.png
      ├─ PREVIEW/labeled_preview.png
      └─ RESULT_INFO.md
```
"""


OUTPUT_FORMAT = """# Output Format Spec

- VFX의 주 납품물은 frame-separated RGBA PNG다. contact sheet는 preview일 뿐 개별 프레임을 대체하지 않는다.
- 모든 VFX 프레임은 GENERATION_SPEC의 canvas, frame count, timing을 따른다.
- 같은 스킬의 모든 프레임은 동일 canvas/pivot/기준축/스케일을 유지한다.
- 실제 alpha 배경이어야 하며 흰색·검정색·체커보드 matte를 넣지 않는다.
- 주요 형상 70%, 외곽 파편/발광 85% 안전영역을 지킨다.
- ICON은 256x256 RGBA 기본 상태 1장이다.
- PNG 안에 텍스트, 번호, UI 프레임, 워터마크, 몬스터 본체를 넣지 않는다.
"""


QUALITY_GATE = """# Art quality gate

패키징 전 실제 PNG로 모두 확인한다.

| Gate | PASS 조건 |
|---|---|
| Intent | monster_id/skill_id/이름/타입/효과/역할 일치 |
| Identity | 해당 몬스터 스킬의 핵심 소재와 실루엣이 읽힘 |
| Rendering | 어두운 외곽, 중간톤 면, 밝은 코어, 입체 재질, 통제된 bloom |
| Alpha | 실제 투명/반투명 alpha, matte/흰 테두리/사각 배경 없음 |
| Motion | 준비→성장→절정→해체→fade가 형상 변화로 보임 |
| Stability | canvas/pivot/축/스케일이 프레임 간 고정 |
| Icon | 64px에서도 읽히며 VFX와 색·형태 언어 공유 |
| Isolation | 텍스트/UI/몬스터 본체/타 스킬 고유 소재 없음 |

한 항목이라도 실패하면 해당 스킬은 FAIL이며 OUTPUT ZIP에 넣지 않는다.
"""


def rebuild_package(source_zip: Path, shared_library: Path, run_id: str) -> dict:
    area_num = re.search(r"AREA_(\d{2})_", source_zip.name).group(1)
    source_hash = sha256_file(source_zip)
    stage = INPUTS / ".rebuild_stage" / f"AREA_{area_num}_IMAGES_INPUT"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    with zipfile.ZipFile(source_zip) as z:
        prefix = f"AREA_{area_num}_IMAGES_INPUT/"
        for name in z.namelist():
            if not name.startswith(prefix) or name.endswith("/"):
                continue
            rel = name[len(prefix):]
            if rel.startswith("global_skill_style_library/"):
                continue
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))

    manifest = parse_manifest(stage)
    area_id = manifest[0]["area_id"]
    area_name = manifest[0]["area_name"]
    for row in manifest:
        spec = stage / row["folder"] / "GENERATION_SPEC.md"
        if not spec.exists():
            raise FileNotFoundError(spec)
        append_assignment(spec, row)
        ensure_runtime_and_provenance(stage / row["folder"], row, source_zip, source_hash, run_id)

    shutil.copytree(shared_library, stage / "global_skill_style_library")
    write_text(stage / "CHATGPT_IMAGES_MASTER_PROMPT.md", master_prompt(area_num, area_name, manifest))
    write_text(stage / "OUTPUT_NAMING_SPEC.md", output_naming(area_num))
    write_text(stage / "OUTPUT_FORMAT_SPEC.md", OUTPUT_FORMAT)
    write_text(stage / "QUALITY_GATE.md", QUALITY_GATE)
    write_text(
        stage / "README_START_HERE.md",
        f"""# START HERE — AREA {area_num} {area_name}

이 ZIP과 같은 폴더의 `AREA_{area_num}_CHATGPT_PRODUCTION_PROMPT.txt`만 일반 ChatGPT에 함께 전달하면 된다. 동일한 프롬프트는 ZIP 내부 `CHATGPT_IMAGES_MASTER_PROMPT.md`에도 들어 있다.

1. `AREA_MANIFEST`에서 확정 WHAT과 대상 {len(manifest)}종을 확인한다.
2. 모든 monster 폴더의 MONSTER_IMAGE와 문서를 읽는다.
3. `global_skill_style_library/area00_finish_baseline`의 실제 PNG는 마감 품질 기준으로 사용한다.
4. `global_skill_style_library`의 MSW 팩 자료는 역할·프레임 구조 기준으로 사용한다.
5. `QUALITY_GATE`, `OUTPUT_NAMING_SPEC`, `OUTPUT_FORMAT_SPEC`를 통과한 실제 PNG와 ZIP을 납품한다.

금지: 기존 AREA 01~20 OUTPUT/실패 샘플을 positive reference로 사용, 기능 재설계, 몬스터 본체 삽입, 포스터형 배경, 가짜 alpha, 개별 프레임 자동 크롭.
""",
    )
    write_text(
        stage / "SOURCE_STATE_CURRENT.md",
        f"""# Input source state

- rebuild run: `{run_id}`
- base canonical package: `docs/art/images-input-packages/{source_zip.name}`
- base package SHA-256: `{source_hash}`
- manifest/monster documents and MONSTER_IMAGE files were preserved from that canonical package, except for the appended reference assignment in GENERATION_SPEC.
- game data was not modified.
- AREA 06 is intentionally retired in the current project design, so operational Area ids are 00~05 and 07~20.
- resource search capture and AREA 00 baseline provenance are inside `global_skill_style_library`.
""",
    )

    hash_rows = []
    for p in sorted(stage.rglob("*")):
        if p.is_file():
            hash_rows.append({"path": p.relative_to(stage).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)})
    write_csv(stage / "INPUT_FILE_HASHES.csv", hash_rows, ["path", "bytes", "sha256"])

    prompt_path = INPUTS / f"AREA_{area_num}_CHATGPT_PRODUCTION_PROMPT.txt"
    write_text(prompt_path, (stage / "CHATGPT_IMAGES_MASTER_PROMPT.md").read_text(encoding="utf-8"))
    target_zip = INPUTS / f"AREA_{area_num}_IMAGES_INPUT.zip"
    temp_zip = INPUTS / f".AREA_{area_num}_IMAGES_INPUT.zip.tmp"
    if temp_zip.exists():
        temp_zip.unlink()
    with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, f"AREA_{area_num}_IMAGES_INPUT/{p.relative_to(stage).as_posix()}")
    last_error = None
    for _ in range(8):
        try:
            temp_zip.replace(target_zip)
            last_error = None
            break
        except OSError as exc:
            last_error = exc
            time.sleep(0.5)
    if last_error is not None:
        raise last_error

    return {
        "area_num": area_num,
        "area_id": area_id,
        "area_name": area_name,
        "monster_count": len(manifest),
        "source_sha256": source_hash,
        "zip_file": target_zip.name,
        "zip_bytes": target_zip.stat().st_size,
        "zip_sha256": sha256_file(target_zip),
        "prompt_file": prompt_path.name,
        "prompt_sha256": sha256_file(prompt_path),
    }


def validate_package(path: Path) -> list[str]:
    errors = []
    area_num = re.search(r"AREA_(\d{2})_", path.name).group(1)
    root = f"AREA_{area_num}_IMAGES_INPUT/"
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            errors.append(f"bad zip member: {bad}")
        names = set(z.namelist())
        required = [
            "README_START_HERE.md", "AREA_MANIFEST.md", "AREA_MANIFEST.csv",
            "CHATGPT_IMAGES_MASTER_PROMPT.md", "OUTPUT_NAMING_SPEC.md", "OUTPUT_FORMAT_SPEC.md",
            "QUALITY_GATE.md", "SOURCE_STATE_CURRENT.md", "INPUT_FILE_HASHES.csv",
            "global_skill_style_library/STYLE_INDEX.md",
            "global_skill_style_library/STYLE_INDEX.csv",
            "global_skill_style_library/summary/STYLE_ATLAS.md",
            "global_skill_style_library/area00_finish_baseline/AREA_OVERVIEW_PREVIEW.png",
        ]
        for rel in required:
            if root + rel not in names:
                errors.append(f"missing {rel}")
        manifest = list(csv.DictReader(io.StringIO(z.read(root + "AREA_MANIFEST.csv").decode("utf-8-sig"))))
        for row in manifest:
            folder = row["folder"] + "/"
            for filename in ["MONSTER_IMAGE.png", "MONSTER_INFO.md", "GENERATION_SPEC.md", "RUNTIME_ROLE_MAP.md", "SOURCE_PROVENANCE.md"]:
                member = root + folder + filename
                if member not in names:
                    errors.append(f"missing {folder}{filename}")
            spec = z.read(root + folder + "GENERATION_SPEC.md").decode("utf-8-sig")
            if "## 이번 개편의 지정 레퍼런스" not in spec:
                errors.append(f"missing reference assignment {folder}")
            image_name = root + folder + "MONSTER_IMAGE.png"
            if image_name in names:
                with Image.open(io.BytesIO(z.read(image_name))) as im:
                    if im.format != "PNG":
                        errors.append(f"not PNG {folder}MONSTER_IMAGE.png")
                    if im.convert("RGBA").getchannel("A").getextrema()[0] == 255:
                        errors.append(f"no transparent pixels {folder}MONSTER_IMAGE.png")
    return errors


def main() -> None:
    now = datetime.now().astimezone()
    run_id = now.strftime("%Y%m%d_%H%M%S")
    recovery_archives = sorted(ARCHIVES.glob("*_before_current_reference_refresh"))
    # Keep the first pre-refresh snapshot as the immutable content baseline.
    # Re-running this builder must not compound generated docs or use a prior
    # failed/successful rebuild as a new visual source.
    recovering = bool(recovery_archives)
    source_root = recovery_archives[0] if recovering else INPUTS
    sources = sorted(source_root.glob("AREA_[0-9][0-9]_IMAGES_INPUT.zip"))
    if not sources:
        raise RuntimeError("No canonical AREA input ZIPs found")
    expected = {f"{n:02d}" for n in range(21)} - {"06"}
    found = {re.search(r"AREA_(\d{2})_", p.name).group(1) for p in sources}
    if found != expected:
        raise RuntimeError(f"Canonical package set mismatch. found={sorted(found)} expected={sorted(expected)}")
    for required in [AREA00_ZIP, AREA00_STYLE, AREA00_OVERVIEW]:
        if not required.exists():
            raise FileNotFoundError(required)

    if recovering:
        archive = source_root
    else:
        archive = ARCHIVES / f"{run_id}_before_current_reference_refresh"
        archive.mkdir(parents=True)
        archive_rows = []
        for p in sorted(INPUTS.iterdir()):
            if p.is_file():
                shutil.copy2(p, archive / p.name)
                archive_rows.append({"file": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)})
        write_csv(archive / "ARCHIVE_HASHES.csv", archive_rows, ["file", "bytes", "sha256"])

    reference_rows = build_reference_cache()
    shared = INPUTS / ".shared_reference_build"
    if shared.exists():
        shutil.rmtree(shared)
    shutil.copytree(REF_CACHE, shared)
    build_area00_baseline(shared / "area00_finish_baseline")

    results = []
    for source in sources:
        results.append(rebuild_package(source, shared, run_id))

    validation = []
    for row in results:
        errors = validate_package(INPUTS / row["zip_file"])
        validation.append({"area_num": row["area_num"], "status": "PASS" if not errors else "FAIL", "errors": errors})
    if any(v["status"] != "PASS" for v in validation):
        write_text(INPUTS / "CURRENT_INPUT_BUILD_VALIDATION.json", json.dumps(validation, ensure_ascii=False, indent=2))
        raise RuntimeError("Validation failed; see CURRENT_INPUT_BUILD_VALIDATION.json")

    columns = list(results[0].keys())
    write_csv(INPUTS / "ALL_AREAS_INDEX.csv", results, columns)
    table = "\n".join(
        f"| {r['area_num']} | {r['area_name']} | {r['monster_count']} | [{r['zip_file']}]({r['zip_file']}) | [{r['prompt_file']}]({r['prompt_file']}) | `{r['zip_sha256']}` |"
        for r in results
    )
    write_text(
        INPUTS / "ALL_AREAS_INDEX.md",
        f"""# AREA 00~20 current image input packages

- build run: `{run_id}`
- operational packages: {len(results)} (AREA 06 is retired and intentionally absent)
- monsters/skills: {sum(r['monster_count'] for r in results)}
- shared resource references: {len(reference_rows)}
- prior canonical files archived at: `{archive.relative_to(ROOT).as_posix()}`
- game data changes: none

각 Area는 ZIP과 같은 번호의 `AREA_XX_CHATGPT_PRODUCTION_PROMPT.txt`를 일반 ChatGPT에 함께 전달한다.

| Area | Name | Skills | Input ZIP | Production prompt | ZIP SHA-256 |
|---:|---|---:|---|---|---|
{table}
""",
    )
    write_text(
        INPUTS / "SEND_TO_CHATGPT_README.md",
        """# ChatGPT 전달 방법

각 Area는 같은 번호의 `AREA_XX_IMAGES_INPUT.zip`과 `AREA_XX_CHATGPT_PRODUCTION_PROMPT.txt`만 함께 사용한다.
일반 ChatGPT에서 ZIP을 첨부하고 prompt 텍스트를 메시지로 보내면 별도의 장문 설명을 다시 작성할 필요가 없다.

prompt에는 입력 문서 읽기 순서, WHAT 고정, AREA 00 마감 기준, MSW 리소스 팩 역할 구조, VFX/ICON 규격, 품질 게이트, preview/manifest/validation/ZIP 납품 요구가 포함되어 있다.

AREA 06은 프로젝트에서 폐기된 지하 하수도 설계이므로 파일이 없다. 현재 운용 Area는 00~05와 07~20이다.
""",
    )
    report = {
        "run_id": run_id,
        "status": "PASS",
        "package_count": len(results),
        "skill_count": sum(r["monster_count"] for r in results),
        "area_06": "RETIRED_NO_PACKAGE",
        "archive": str(archive),
        "reference_count": len(reference_rows),
        "validation": validation,
        "packages": results,
    }
    write_text(INPUTS / "CURRENT_INPUT_BUILD_REPORT.json", json.dumps(report, ensure_ascii=False, indent=2))
    write_text(INPUTS / "CURRENT_INPUT_BUILD_VALIDATION.json", json.dumps(validation, ensure_ascii=False, indent=2))
    write_text(
        INPUTS / "CURRENT_INPUT_BUILD_REPORT.md",
        f"""# Current AREA input rebuild report

- run: `{run_id}`
- status: **PASS**
- 20 operational Area ZIPs and 20 ready-to-send prompts rebuilt.
- AREA 06 is the retired sewer design and was not invented or regenerated.
- {sum(r['monster_count'] for r in results)} monster/skill placements preserved from the canonical package manifests.
- Existing game data and output ZIPs were not modified.
- Previous canonical inputs were copied to `{archive.relative_to(ROOT).as_posix()}` with SHA-256 records.
- The 183-entry undated style dump was replaced by {len(reference_rows)} curated, named resource-pack references plus the actual AREA 00 finish baseline.
- Every package passed ZIP integrity, required-document, monster-document, MONSTER_IMAGE PNG/alpha, prompt, and reference-assignment checks.
""",
    )
    shutil.rmtree(INPUTS / ".rebuild_stage", ignore_errors=True)
    shutil.rmtree(shared, ignore_errors=True)
    print(json.dumps({"status": "PASS", "run_id": run_id, "packages": len(results), "skills": sum(r["monster_count"] for r in results), "archive": str(archive)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
