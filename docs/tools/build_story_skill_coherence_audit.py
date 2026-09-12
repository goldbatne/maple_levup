from __future__ import annotations

import csv
import hashlib
import io
import textwrap
import zipfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "docs" / "art"
AUDIT = ART / "output_audit"
REPACK = ART / "output_repacked" / "20260912_153221_v24_repack"
REPACK_WORK = ART / "output_audit_work" / "20260912_153221_v24_repack" / "STAGING"
CONTENT_RUN = AUDIT / "runs" / "20260912_145815_content_style"
RUN_ID = "20260912_160012_story_skill_coherence_r5"
RUN = AUDIT / "runs" / RUN_ID
EVIDENCE = RUN / "evidence"

BASELINE_HASHES = {
    "AREA_01_IMAGES_OUTPUT.zip": "fe273429b4798491f02bf0274ba74214c8e1e28aca5b994c174bf77568d34023",
    "AREA_02_IMAGES_OUTPUT.zip": "3961030e37ced705bc0a80d983e170da0e9f05fc8fe9f96df26f09944e40228d",
    "AREA_03_IMAGES_OUTPUT.zip": "18dfd00a7a17d7aac7b0700ea558a04ecd8f5cb654ea5d111a8ff4611bbf638f",
    "AREA_04_IMAGES_OUTPUT.zip": "0749c2d0fae8966f748b8c62a6559612ea5d9572564c479b024f229405f31e10",
    "AREA_05_IMAGES_OUTPUT.zip": "d8f29aca689b5969e528815fcdfcfad499dbdcc6ec11e75ad2a7b5edfabadb2d",
    "AREA_07_IMAGES_OUTPUT.zip": "8af08f4a2d8cc1d187ceb4566820b0d6e31423cb60d3c2eb53a1c9021a821fa1",
    "AREA_08_IMAGES_OUTPUT.zip": "deb1e6180851f0de755b157cbca863c01612c129148f66b38c1462d3328ac6b7",
    "AREA_09_IMAGES_OUTPUT.zip": "5492ea6aa2f3fe761473f6cd96150d314127fbeea9232de8ca68b774c96f7fd8",
    "AREA_10_IMAGES_OUTPUT.zip": "68d6caaeb6a59f418e5e373b0b3990829c360d2aa6aaa824f9f29d6e29627973",
    "AREA_13_IMAGES_OUTPUT.zip": "667d3343bcfc5c6d214c484408e8bdd19afefd42776005a8c8b6659f3b29f116",
    "AREA_14_IMAGES_OUTPUT.zip": "a53e4b5603dcaf15e9818b70ef8022feee598d4e474fdce3034f144384914e5d",
    "AREA_15_IMAGES_OUTPUT.zip": "d235e524a78c1ddfb22367876ce2ad4382e8b27c47e4f13e43f8201c32402c05",
    "AREA_16_IMAGES_OUTPUT.zip": "68f6a09e25e8ddb2c69d0eef6b9ea07207738fbf18b441f9018f48d228a67886",
    "AREA_17_IMAGES_OUTPUT.zip": "aa91d2f2ca5767c074a7f3c7b97e4983894cbe2885b10e0969b6b11c604803ab",
    "AREA_18_IMAGES_OUTPUT.zip": "ec606ee490ccb64a96f0619011b7b272f707d00f059660ed987b32c6a5846655",
    "AREA_19_IMAGES_OUTPUT.zip": "69ac7d9eee96a3dfe869ff3bdfbf6ffd7cd122535fed7503029ff43423584c5b",
    "AREA_20_IMAGES_OUTPUT.zip": "dc66834bba548fb5ed49c1460f73716d77041c2019c154d76d4ac3765f9a8434",
}

FINDINGS = {
    ("area_02", "m_stone_golem"): {
        "status": "REGION_MISMATCH",
        "title": "스톤골렘 — 페리온 배치",
        "project": "프로젝트: area_02 페리온, 스킬 ‘암석 피부’. VFX는 암석판 방패와 금빛 균열광.",
        "external": "외부 확인: 스톤골렘은 헤네시스 골렘의 사원 몬스터로 기록됨.",
        "source": "https://maplestorywiki.net/w/Golem%27s_Temple_Entrance (편집 시점 불명, 검색 확인 2026-09-12); 넥슨 2011 지역 개편 아카이브(시점 2011-07-07)도 헤네시스 몬스터로 기재.",
        "inference": "스킬명·효과·아트는 몬스터와 맞지만 Area 귀속만 원작과 다르다. 원화 재생성 사유는 아니다.",
        "unknown": "프로젝트가 페리온의 암석 테마를 우선한 의도적 재배치인지 확정 기록 없음.",
    },
    ("area_03", "m_bubbling"): {
        "status": "REGION_MISMATCH",
        "title": "버블링 — 엘리니아 배치",
        "project": "프로젝트: area_03 엘리니아, 패시브 ‘물방울 마력’. 아트는 기포·거품 고리.",
        "external": "외부 확인: 버블링은 커닝시티 지하철 계열 몬스터로 기록됨.",
        "source": "https://maplestorywiki.net/w/Kerning_City (편집 시점 불명, 검색 확인 2026-09-12); 넥슨 아카이브 이용자 기록(2008~2010년대)도 지하철 1호선 배치를 반복 기재.",
        "inference": "스킬명·효과·아트는 버블링과 자연스럽지만 엘리니아 서사 연결은 약하다. 원화 재생성 사유는 아니다.",
        "unknown": "엘리니아로 옮긴 별도 프로젝트 서사는 확인되지 않음.",
    },
    ("area_05", "m_king_clang"): {
        "status": "NEEDS_USER_REVIEW",
        "title": "킹크랑 — 노틸러스/플로리나 경계",
        "project": "프로젝트: area_05 노틸러스 보스, 스킬 ‘왕게의 집게 파도’. 아트는 붉은 집게와 파도 충격.",
        "external": "외부 확인: 넥슨 2007 업데이트는 킹크랑을 플로리나 비치 마스터 몬스터로 명시.",
        "source": "https://archive.maplestory.nexon.com/News/Update/51 (게시 2007-08-16, 검색 확인 2026-09-12); 플로리나 비치는 이후 노틸러스 해변에서 연결된 시기도 있음(시점 자료 혼재).",
        "inference": "엄밀한 원작 Area 명칭은 다르지만, 인접 해안·과거 연결 동선과 해양 테마는 자연스럽다. 유지 여부는 지역 단위의 엄밀성 기준에 달림.",
        "unknown": "프로젝트가 노틸러스 권역에 플로리나 비치를 포함한다고 정의했는지 명시 문서 미확인.",
    },
    ("area_20", "m_mutant_stone_mask"): {
        "status": "SKILL_NAME_MISMATCH",
        "title": "변형된 스톤마스크 — ‘발굴지의 석면’",
        "project": "프로젝트: 패시브 ‘발굴지의 석면’. VFX·ICON은 갈색 암석판/가면판이 맞물리는 방호 표현.",
        "external": "외부 확인: ‘석면(石綿)’은 asbestos, 즉 섬유상 규산염 광물류를 뜻한다.",
        "source": "https://www.law.go.kr/LSW/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000472561 (석면안전관리법 시행 2025-10-01); 넥슨 황혼의 페리온 업데이트 2013-02-21은 변형된 스톤마스크와 발굴지역을 확인.",
        "inference": "현재 그림은 섬유상 석면이 아니라 돌판/가면 표면을 표현하므로, 이름의 일반적 의미가 시각과 충돌한다. 아트보다 스킬명 검토 대상.",
        "unknown": "‘석면’을 ‘돌의 면(面)’이라는 창작 합성어로 의도했는지 기록 없음.",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def checker(size: tuple[int, int], cell: int = 16) -> Image.Image:
    im = Image.new("RGBA", size, (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            c = (231, 234, 238, 255) if (x // cell + y // cell) % 2 else (250, 251, 252, 255)
            d.rectangle((x, y, min(x + cell, size[0]), min(y + cell, size[1])), fill=c)
    return im


def contain(im: Image.Image, box: tuple[int, int]) -> Image.Image:
    src = im.convert("RGBA")
    src.thumbnail(box, Image.Resampling.LANCZOS)
    bg = checker(box)
    bg.alpha_composite(src, ((box[0] - src.width) // 2, (box[1] - src.height) // 2))
    return bg.convert("RGB")


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width_chars: int, fnt, fill, spacing=8) -> int:
    y = xy[1]
    for line in textwrap.wrap(text, width=width_chars, break_long_words=True, break_on_hyphens=False) or [""]:
        draw.text((xy[0], y), line, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def role_paths(area: str, monster: str) -> list[Path]:
    mapping = REPACK / "PNG_BYTE_PRESERVATION.csv"
    rows = list(csv.DictReader(mapping.open(encoding="utf-8-sig", newline="")))
    selected = [r for r in rows if r["area_id"] == area and r["monster_id"] == monster]
    by_role: dict[str, list[dict]] = {}
    for row in selected:
        by_role.setdefault(row["role"], []).append(row)
    result: list[Path] = []
    for role in ("ICON", "CAST_VFX", "PROJECTILE", "REFERENCE_VFX"):
        group = sorted(by_role.get(role, []), key=lambda r: int(r.get("frame_index") or 0))
        if not group:
            continue
        picks = group if role == "ICON" else [group[0], group[len(group) // 2], group[-1]]
        for row in picks:
            result.append(REPACK_WORK / f"AREA_{area[-2:]}_IMAGES_OUTPUT" / Path(row["output_path"]))
    return result


def monster_image(area: str, monster: str) -> Image.Image | None:
    idx = list(csv.DictReader((AUDIT / "BASELINE_INDEX.csv").open(encoding="utf-8-sig", newline="")))
    row = next((r for r in idx if r.get("area_id") == area and r.get("kind") == "AREA_INPUT"), None)
    if not row:
        return None
    with zipfile.ZipFile(row["path"]) as zf:
        candidates = [n for n in zf.namelist() if monster in n and "MONSTER_IMAGE" in n and n.lower().endswith(".png")]
        if not candidates:
            return None
        return Image.open(io.BytesIO(zf.read(candidates[0]))).convert("RGBA")


def build_finding_board(area: str, monster: str, item: dict) -> Path:
    canvas = Image.new("RGB", (1900, 980), "#eef2f7")
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 0, 1900, 92), fill="#172334")
    d.text((36, 24), f"{area.upper()} · {item['title']} · {item['status']}", font=font(32, True), fill="white")
    y = 130
    for label, value, color in (
        ("[프로젝트 자료]", item["project"], "#244b76"),
        ("[외부 확인 사실]", item["external"], "#8a3b12"),
        ("[출처/시점]", item["source"], "#4a5568"),
        ("[추정·판단]", item["inference"], "#6b3e85"),
        ("[미확인]", item["unknown"], "#6b7280"),
    ):
        d.text((36, y), label, font=font(22, True), fill=color)
        y = draw_wrapped(d, (230, y), value, 34, font(21), "#172334", 7) + 16
    d.line((950, 112, 950, 948), fill="#b5c0ce", width=3)
    imgs: list[tuple[str, Image.Image]] = []
    mi = monster_image(area, monster)
    if mi is not None:
        imgs.append(("INPUT MONSTER", mi))
    for p in role_paths(area, monster):
        if p.exists():
            imgs.append((p.parent.name + " / " + p.stem.split("_")[-1], Image.open(p).convert("RGBA")))
    x0, y0 = 990, 145
    for i, (label, im) in enumerate(imgs[:7]):
        col, row = i % 3, i // 3
        x, yy = x0 + col * 285, y0 + row * 275
        canvas.paste(contain(im, (245, 210)), (x, yy))
        d.text((x, yy + 218), label[:28], font=font(16, True), fill="#27364a")
    out = EVIDENCE / f"{area.upper()}_{monster}_STORY_SKILL.png"
    canvas.save(out, optimize=True)
    return out


def build_hold_board(area: int, title: str, lines: list[str], source_image: Path, out_name: str) -> Path:
    src = Image.open(source_image).convert("RGB")
    src.thumbnail((2120, 620), Image.Resampling.LANCZOS)
    h = 390 + src.height
    canvas = Image.new("RGB", (2200, h), "#eef2f7")
    d = ImageDraw.Draw(canvas)
    d.rectangle((0, 0, 2200, 90), fill="#172334")
    d.text((34, 23), f"AREA {area:02d} · {title}", font=font(34, True), fill="white")
    y = 120
    for line in lines:
        y = draw_wrapped(d, (40, y), line, 112, font(22), "#172334", 7) + 8
    canvas.paste(src, ((2200 - src.width) // 2, h - src.height - 24))
    out = EVIDENCE / out_name
    canvas.save(out, optimize=True)
    return out


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=False)
    EVIDENCE.mkdir()

    baseline_rows = []
    for name, expected in BASELINE_HASHES.items():
        path = REPACK / name
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"baseline hash changed: {name} {actual} != {expected}")
        baseline_rows.append({
            "kind": "AREA_OUTPUT_REPACK_BASELINE",
            "area_id": "area_" + name[5:7],
            "revision": "V2.4_REPACK_20260912_153221",
            "status": "PACKAGE_VALIDATION_PASS_ART_PENDING_RUNTIME_NOT_RUN",
            "path": str(path),
            "sha256": actual,
            "fixed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        })
    with (AUDIT / "BASELINE_OUTPUT_INDEX.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(baseline_rows[0]))
        w.writeheader(); w.writerows(baseline_rows)

    content_rows = list(csv.DictReader((CONTENT_RUN / "CONTENT_STYLE_REVIEW.csv").open(encoding="utf-8-sig", newline="")))
    rows = []
    for r in content_rows:
        if r["area_id"] in {"area_11", "area_12"}:
            continue
        key = (r["area_id"], r["monster_id"])
        finding = FINDINGS.get(key)
        rows.append({
            "area_id": r["area_id"],
            "area_name": r["area_name"],
            "monster_id": r["monster_id"],
            "monster_name": r["monster_name"],
            "skill_id": r["skill_id"],
            "skill_name": r["skill_name"],
            "skill_type": r["skill_type"],
            "story_skill_status": finding["status"] if finding else "NO_OBVIOUS_ISSUE",
            "project_evidence": finding["project"] if finding else "승인 INPUT V2.4의 확정 스킬/역할과 기존 전체 프레임·ICON 시각 대조를 재사용.",
            "external_fact": finding["external"] if finding else "외부 사실을 추가로 단정하지 않음; 창작 스킬명 자체는 오류로 처리하지 않음.",
            "inference": finding["inference"] if finding else "몬스터·지역 핵심 소재와 스킬명/효과/실제 아트 사이에 명백한 충돌 없음.",
            "unknown": finding["unknown"] if finding else "동일한 원작 공식 스킬명의 존재 여부는 판정 기준이 아님.",
            "visual_evidence_reuse": "REUSED: previous full-frame+ICON review; repack role PNG SHA-256 unchanged",
            "user_approved": "NO",
        })
    if len(rows) != 89:
        raise RuntimeError(f"expected 89 completed-area entries, got {len(rows)}")
    with (RUN / "STORY_SKILL_REVIEW.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    finding_images = {}
    for (area, monster), item in FINDINGS.items():
        finding_images[(area, monster)] = build_finding_board(area, monster, item)

    hold11 = build_hold_board(
        11,
        "킹 블록퍼스 CAST·PROJECTILE 수정 방향",
        [
            "확정 핵심 소재: 왕관 블록이 회전하며 각진 에너지 조각을 발사하는 탄. 몬스터 본체는 VFX에 직접 넣지 않는다.",
            "CAST(8×384, 0.10s): 시전자 원점에서 왕관 블록과 각진 금·자주 조각이 조립→방출 섬광→잔광. 몸·눈·얼굴·포신 형태를 제거한다. 우측 기준/FlipX는 CAST에만 적용한다.",
            "PROJECTILE(4×384, 0.08s): 왕관 블록 핵+소수 각진 조각만 남긴 방향 중립 비행체. 로컬 상대 회전만 허용; 전체 이동·Z회전은 엔진 담당. 0.32초 non-loop로 0.35초 수명 안에 완주한다.",
            "유지: ICON 및 AREA 11의 다른 몬스터 정상 에셋. 신규 HIT/IMPACT 역할은 만들지 않는다.",
        ],
        REPACK / "HOLD_EVIDENCE" / "AREA_11_m_king_bloctopus_CAST_PROJECTILE.png",
        "AREA_11_KING_BLOCTOPUS_CORRECTION_DIRECTION.png",
    )
    hold12 = build_hold_board(
        12,
        "장난감 목마 GENERATION_SPEC vs 실제 CAST",
        [
            "허용(CAST 핵심): ‘목마 바퀴와 태엽이 전방으로 겹치는 장난감 돌진선’. 이동 궤적 전체를 한 프레임 안에서 재현하지 않는다.",
            "허용(ICON 전용): 대표 실루엣 ‘목마 머리’ + 보조 효과 ‘바퀴 속도선’.",
            "금지(VFX): ‘몸·얼굴·전신 실루엣은 VFX에 넣지 않는다’, ‘몬스터 본체를 VFX 안에 직접 그리지 않는다’.",
            "실제 CAST: 눈 달린 목마 머리/상체가 F00~F04의 중심 실루엣이다. ICON의 목마 머리 허용은 CAST 허용으로 쓰여 있지 않으므로 현행 문구 기준 명시적 금지 위반이다. 사용자가 ‘장난감 부품’ 예외로 재해석할 때만 유지 가능하다.",
        ],
        REPACK / "HOLD_EVIDENCE" / "AREA_12_m_toy_trojan_CAST.png",
        "AREA_12_TOY_TROJAN_SPEC_VS_CAST.png",
    )

    report = [
        "# REPACK 기준 OUTPUT — 스토리·스킬명 보완 검수",
        "",
        f"- 실행: `{RUN_ID}`",
        f"- 고정 OUTPUT: `{REPACK}`",
        "- 고정 조건: 17 ZIP SHA-256 일치, 역할 PNG 839개 바이트 변경 0건인 REPACK 결과만 기존 구조·규격·스타일 검사를 재사용",
        "- 이번 검사: 17 Area / 89 몬스터·스킬의 원작·지역 설정 ↔ 확정 스킬명·효과 ↔ 실제 VFX·ICON 연결",
        "- 재실행하지 않은 검사: 동일 INPUT V2.4와 동일 PNG 해시에 대한 구조·PNG 규격·스타일 전수 검사",
        "- 변경: 원화·ZIP·INPUT·게임 파일 없음",
        "",
        "## 결과",
        "",
        "- 명백한 추가 불일치: 3건 (스톤골렘 지역, 버블링 지역, ‘발굴지의 석면’ 명칭)",
        "- 사용자 판단: 1건 (킹크랑을 노틸러스 권역에 포함할지)",
        "- 위 4건을 제외한 명백한 문제 없음: 85건",
        "- 완료 17 Area에서 스토리·명칭 때문에 원화 재생성이 필요한 항목: 0건",
        "- 이전 ‘검토 필요’ 정정: 도도의 ‘기억 포식’은 실제 설정과 일치; ‘검은 뿌리의 묘지’는 공식 황혼의 페리온 맵명 ‘칼바람의 묘지’와 충돌하지 않음",
        "",
        "## 새로 확인된 불일치·판단 항목",
        "",
    ]
    for (area, monster), item in FINDINGS.items():
        report += [
            f"### {area} / {monster} — {item['title']} (`{item['status']}`)",
            "",
            f"- [프로젝트 자료] {item['project']}",
            f"- [외부 확인 사실] {item['external']}",
            f"- [출처·시점] {item['source']}",
            f"- [추정·판단] {item['inference']}",
            f"- [미확인] {item['unknown']}",
            f"- 근거 이미지: `{finding_images[(area, monster)]}`",
            "",
        ]
    report += [
        "## AREA 11·12 보류",
        "",
        "### AREA 11",
        "",
        "- 킹 블록퍼스의 ICON과 다른 정상 에셋은 유지한다.",
        "- CAST·PROJECTILE만 위 수정 계약으로 원화 수정 후보를 유지한다.",
        f"- 근거/수정 방향: `{hold11}`",
        "",
        "### AREA 12",
        "",
        "- 현행 문구만 적용하면 실제 CAST는 명시적 금지 위반이다. 목마 머리 허용은 ICON 항목에만 있다.",
        "- 사용자 판단은 ‘눈 달린 머리/상체를 장난감 부품 예외로 허용하도록 명세를 바꿀 것인가’에만 남는다. 현행 명세를 유지하면 CAST 원화 수정 후보이다.",
        f"- 나란히 비교: `{hold12}`",
        "",
        "## 출처 신뢰도와 시점",
        "",
        "- 우선: 넥슨 공식 업데이트/아카이브(게시일 기록).",
        "- 보조: MapleStory Wiki/StrategyWiki(편집 시점이 표시되거나 시점 불명인 경우 그대로 기록).",
        "- 프로젝트 창작 스킬은 동일한 공식 스킬명의 존재를 요구하지 않았다.",
        "- 외부 근거가 없는 능력 서사는 ‘창작’으로만 분류했으며, 몬스터·지역·실제 아트와 충돌하지 않으면 오류로 올리지 않았다.",
        "",
        "## 상태 경계",
        "",
        "이 검수는 재생성 결정을 위한 자료다. USER_APPROVED, 런타임 PASS, 게임 반입 완료를 의미하지 않는다.",
    ]
    (RUN / "STORY_SKILL_SUMMARY.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (AUDIT / "LATEST_REPORT.md").write_text(
        f"# Latest output audit\n\n- `{RUN / 'STORY_SKILL_SUMMARY.md'}`\n",
        encoding="utf-8",
    )
    print(f"run={RUN}")
    print(f"reviewed={len(rows)} no_issue={len(rows)-len(FINDINGS)} findings={len(FINDINGS)}")
    print(f"baseline_zips={len(baseline_rows)}")


if __name__ == "__main__":
    main()
