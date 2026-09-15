from pathlib import Path
import base64
import csv
import datetime
import hashlib
import io
import json
import re
import zipfile

from PIL import Image, ImageOps

BASE = Path(__file__).parent.parent / "images-input-packages"
COLLECTION = Path(__file__).parent
ZIP_PATH = BASE / "AREA_00_IMAGES_INPUT.zip"
TXT_PATH = BASE / "AREA_00_CHATGPT_PRODUCTION_PROMPT.txt"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def png_bytes(image):
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


def contact_board(entries, cols=4, rows=4):
    size = 1024
    cell = size // cols
    board = Image.new("RGB", (size, size), (42, 42, 46))
    manifest = []
    for index, entry in enumerate(entries[: cols * rows]):
        image = Image.open(io.BytesIO(entry["bytes"])).convert("RGBA")
        contained = ImageOps.contain(image, (cell - 24, cell - 24), Image.Resampling.LANCZOS)
        tile = Image.new("RGBA", (cell, cell), (42, 42, 46, 255))
        x = (cell - contained.width) // 2
        y = (cell - contained.height) // 2
        tile.alpha_composite(contained, (x, y))
        col = index % cols
        row = index // cols
        board.paste(tile.convert("RGB"), (col * cell, row * cell))
        manifest.append(
            {
                "tile": index,
                "row": row,
                "column": col,
                "source_path": entry["path"],
                "source_sha256": sha(entry["bytes"]),
                "purpose": entry["purpose"],
            }
        )
    return png_bytes(board), manifest


def balanced_representatives(elements, limit=16):
    groups = [list(e.get("representative_frames", [])) for e in elements if e.get("representative_frames")]
    result = []
    while groups and len(result) < limit:
        remaining = []
        for group in groups:
            if group and len(result) < limit:
                result.append(group.pop(0))
            if group:
                remaining.append(group)
        groups = remaining
    return result


def parse_skill_spec(data, folder):
    text = decode(data[folder + "/GENERATION_SPEC.md"])
    material = re.search(r"^- 핵심 소재:\s*(.+)$", text, re.M).group(1)
    colors = [m.group(1) for m in re.finditer(r"^- (?:주 색상|보조 색상):\s*(.+)$", text, re.M)]
    vfx = re.search(r"^- VFX:\s*(\d+) frames, 각 (\d+)×(\d+) RGBA PNG, 약 ([\d.]+) sec/frame", text, re.M)
    icon = re.search(r"^- ICON:\s*(.+)$", text, re.M).group(1)
    return {
        "material": material,
        "colors": colors,
        "frames": int(vfx.group(1)),
        "width": int(vfx.group(2)),
        "height": int(vfx.group(3)),
        "seconds": float(vfx.group(4)),
        "icon": icon,
    }


def prompt_text(rows, specs):
    table = []
    for row in rows:
        spec = specs[row["skill_id"]]
        table.append(
            f'| {int(row["work_order"]):03d} | {row["monster_name"]} / `{row["monster_id"]}` | '
            f'{row["skill_name"]} / `{row["skill_id"]}` | {row["skill_type"]} | '
            f'{spec["frames"]}× VFX + ICON 1 | `{row["folder"]}/DESIGN_REFERENCE_BRIEF.md` |'
        )
    total = sum(specs[r["skill_id"]]["frames"] for r in rows)
    return f'''# AREA 00 신규 제작 실행 명령 — 단일 스킬 파이프라인

이 TXT와 `AREA_00_IMAGES_INPUT.zip`을 첨부한 사용자가 “첨부한 프롬프트대로 실행해줘”라고 요청하면, 아래 작업을 실제로 수행한다. 계획·검수 보고·실패 시안 ZIP으로 대체하지 않는다.

## 0. 납품 계약

목표는 기존 OUTPUT을 덮어쓰지 않고 `AREA_00_IMAGES_OUTPUT/`을 새로 제작하는 것이다.

- 대상: 5스킬
- 필수 VFX: 총 {total}장의 frame-separated 256×256 RGBA PNG
- 필수 ICON: 256×256 RGBA PNG 5장
- 추가 필수: Area 전체 preview/labeled preview, 몬스터별 contact/labeled preview, 재생 HTML, manifest, 검증 기록, reference 기록, result info
- 최종 파일: `AREA_00_IMAGES_OUTPUT.zip`
- 상태: `REVIEW_CANDIDATE`; USER_APPROVED나 게임 반입 완료로 기록하지 않는다.

필수 자산이 하나라도 없거나 아트 게이트가 실패하면 정상 이름의 OUTPUT ZIP을 만들지 않는다. `_FAILED_GENERATION_CANDIDATE`를 넣은 ZIP, 보고서만 든 ZIP, 이미지 한 장짜리 ZIP을 납품하지 않는다. 원화 생성 기능이 실제로 막힌 경우에는 실패 증빙을 ZIP 밖의 별도 경로에 보존하고, 무엇이 미완료인지 사용자에게 직접 알린다.

## 1. 지침의 우선순위

1. 이 TXT와 ZIP 내부 `CHATGPT_IMAGES_MASTER_PROMPT.md` — 두 파일은 같은 내용이며 실행 절차의 최종 권위다.
2. `AREA_MANIFEST.csv/.md` — 몬스터·스킬 ID, 이름, 타입, 실제 효과·동작
3. 각 `RUNTIME_ROLE_MAP.md`와 `GENERATION_SPEC.md` — 필수 NEW_ART, 소재, 팔레트, 프레임·캔버스·타이밍
4. 각 `DESIGN_REFERENCE_BRIEF.md`와 `reference_resource_design/prepared_boards/` — 실제 이미지 참조와 적용/제외 범위
5. `OUTPUT_NAMING_SPEC.md`, `OUTPUT_FORMAT_SPEC.md`, `QUALITY_GATE.md` — 파일과 검증 규격

그 밖의 공통 스타일 설명은 보조 자료다. 위 문서와 충돌하는 예전의 광범위 참조 지정, “시간 구조만 참고”, Area 전체 동시 생성, 참조 입력 확인 불가를 즉시 중단 사유로 삼는 문구는 적용하지 않는다.

## 2. 고정 작업 목록

| 순번 | 몬스터 | 스킬 | 타입 | 필수 산출 | 실제 참조 brief |
|---:|---|---|---|---|---|
{chr(10).join(table)}

monster_id, skill_id, 이름, 타입, 실제 효과·동작, 소재, 팔레트, 방향, 프레임 수를 바꾸지 않는다. MONSTER_IMAGE는 색·재질·부위 모티브를 확인하는 참조다. 몬스터 몸·얼굴·캐릭터를 VFX나 ICON에 직접 넣지 않는다.

## 3. 생성 전에 실제로 열 파일

ZIP을 풀고 다음을 실제로 읽고 이미지로 연다.

1. `README_START_HERE.md`, AREA_MANIFEST, 출력 규격과 품질 게이트
2. 다섯 몬스터의 MONSTER_IMAGE, MONSTER_INFO, GENERATION_SPEC, RUNTIME_ROLE_MAP, DESIGN_REFERENCE_BRIEF
3. 각 brief가 지정한 공식 원본 PNG/GIF와 전체 연속 PNG
4. `global_skill_style_library/area00_finish_baseline/full_vfx_frames/`의 기존 승인 00 전체 44프레임과 ICON
5. 각 스킬의 `prepared_boards/*_OFFICIAL_VFX_BOARD.png`, `*_AREA00_FINISH_BOARD.png`, 대응 BOARD_MANIFEST.json

준비 보드는 원본 이미지들을 보기 좋게 배치한 전달용 합성물이다. 생성 결과가 아니며, 보드의 회색 배경·격자·공식 스킬 고유 모양을 OUTPUT에 복제하지 않는다. BOARD_MANIFEST의 원본 경로와 SHA-256으로 실제 구성 파일을 추적한다.

## 4. 참조 이미지를 실제 생성 호출에 전달하는 법

한 스킬의 VFX 생성 호출마다 다음 세 종류를 실제 reference image input으로 전달한다.

- 해당 폴더의 원본 `MONSTER_IMAGE.png` 1장
- 해당 skill_id의 `OFFICIAL_VFX_BOARD.png` 1장
- 해당 skill_id의 `AREA00_FINISH_BOARD.png` 1장

도구가 여러 이미지를 직접 받을 수 있으면 세 이미지를 개별 입력한다. 한 장만 받을 수 있으면 세 이미지를 고해상도 참조 보드 한 장으로 기계적으로 결합한 뒤 그 보드를 실제 입력한다. 파일 경로를 프롬프트 문장에 쓰거나 이미지를 화면에 표시하는 것だけ으로 입력 완료라고 하지 않는다.

준비 보드에는 각 스킬에 적합한 공식 효과의 여러 단계와 승인 00 마감 프레임이 들어 있다. 먼저 원본 연속 프레임 전체를 관찰하고, 실제 호출에는 준비 보드를 사용한다. 참조를 더 줄여야 할 때는 준비/성장/절정/해체/fade와 재질 면을 모두 남기며 선택 근거를 기록한다. 관련 없는 다른 스킬 참조를 추가하지 않는다.

도구가 내부 모델명이나 개별 파일 수신 목록을 노출하지 않더라도, 준비 보드를 실제 이미지 입력으로 전달했고 그 보드의 SHA-256을 기록할 수 있으면 제작을 중단하지 않는다. 기록은 다음처럼 구분한다.

- 생성 도구: `native image generation/editing — version/model unverified`
- `REFERENCE_BOARD_USED=true/false`
- 보드 경로와 SHA-256
- `TOOL_INTERNAL_REFERENCE_AUDIT=UNAVAILABLE`일 수 있음

보드를 실제 입력하지 않았다면 USED=true라고 쓰지 않는다.

## 5. 생성 단위 — Area 전체 동시 생성 금지

절대로 다섯 몬스터·다섯 스킬을 한 이미지에 생성하지 않는다. 하나의 생성 작업에는 한 monster_id와 한 skill_id만 존재해야 한다. 이미지 안에는 텍스트, 번호, 단계명, 행 라벨, UI 패널, 캐릭터, 몬스터 본체, 다른 스킬, ICON을 함께 넣지 않는다.

### 5-1. 첫 스킬 파이프라인 게이트

먼저 `001 / m_snail / s_mon_snail_dew_trail`만 제작한다. 사용자 중간 승인은 요구하지 않지만 다음 항목을 모두 통과해야 002로 진행한다.

- 실제 몬스터·공식 VFX 보드·AREA00 마감 보드가 생성 호출에 전달됨
- 이슬·점액의 낮은 지면 흐름으로 읽히고 물 폭발이나 달팽이 캐릭터가 되지 않음
- 프레임 수·캔버스·알파·축이 명세와 일치
- 어두운 유색 면 → 분명한 중간톤 → 제한된 밝은 코어와 반투명 가장자리가 있음
- 준비→성장→절정→해체→fade가 실제 형상 변화로 이어짐

첫 생성이 실패하면 그 이미지를 다른 스킬의 참조로 사용하지 않는다. 실패 원인을 `shape/material/motion/alpha/layout/contamination`으로 구분하고, 실패한 조건을 직접 고친 프롬프트 또는 생성 방식으로 001만 다시 만든다. 같은 문구와 같은 방식의 맹목적 재시도는 금지한다. 파이프라인이 통과하지 않았는데 002~005나 Area 전체 이미지를 생성하지 않는다.

### 5-2. 스킬별 VFX 원화 제작

통과 후 002→005 순서로 한 스킬씩 진행한다. 권장 기본 방식은 스킬 하나의 무라벨 투명 source sheet를 만든 뒤 고정 좌표로 분리하는 것이다.

- 8프레임: 1024×1024 source sheet 안에 4열×2행의 동일 크기 정사각 셀을 배치한다. 위·아래 여백은 허용하지만 셀 사이 형상이 닿으면 안 된다.
- 12프레임: 1024×1024 source sheet 안에 4열×3행의 동일 크기 정사각 셀을 배치한다.
- 각 셀에는 동일한 VFX의 연속 단계 한 개만 둔다. 글자·번호·몬스터·배경·ICON·프레임 테두리를 넣지 않는다.
- 목표 축과 피봇은 sheet 전체에서 고정하고, 개별 셀 자동 크롭이나 개별 중앙 맞춤을 하지 않는다.

8프레임의 흐름은 F00 출현, F01 준비, F02 성장, F03 절정 직전, F04 절정, F05 해체 시작, F06 조각·잔상, F07 fade다. 12프레임은 준비 2, 성장 3, 절정 2, 해체 3, fade 2프레임으로 실제 형태를 연결한다. alpha만 낮추거나 동일 그림을 확대·축소해 애니메이션을 대신하지 않는다.

source sheet가 셀 분리·축·몬스터 혼입 문제로 한 번 실패하면 같은 sheet 지시를 반복하지 않는다. 대체 방식으로 절정 프레임을 먼저 만들고, 그 프레임과 같은 참조를 사용한 native image editing으로 준비·성장·해체 프레임을 개별 또는 2프레임 단위로 만든다. 각 프레임은 실제 형상이 변해야 한다. Python/Pillow/SVG/Canvas로 원화를 새로 그리거나 단순 보간해서 채우지 않는다.

source sheet에서 추출할 때만 Python 등 기계적 도구를 사용할 수 있다. 셀 좌표, source SHA-256, 추출 좌표, 리사이즈와 공통 등록 변환을 기록한다. 옆 셀 조각·절단·라벨이 섞인 셀은 추출로 억지로 살리지 않고 해당 스킬 원화를 다시 만든다.

### 5-3. ICON 제작

해당 스킬 VFX가 모두 통과한 다음 ICON을 별도로 만든다. ICON 호출에는 다음을 실제 입력한다.

- 해당 MONSTER_IMAGE
- 완성 VFX의 준비/절정/해체 대표 프레임
- brief가 지정한 공식 ICON 원본
- 기존 승인 00 ICON

ICON은 VFX의 고정 핵심 모티브를 256×256 한 장에 압축한다. 공식 ICON의 명암 분리와 64px 읽힘을 참고하지만 공식 UI 프레임, 글자, 숫자, 캐릭터 얼굴, 몬스터 몸을 복제하지 않는다. ICON도 실제 투명 RGBA 기본 상태만 만들며 disabled/mouseover를 임의 추가하지 않는다.

## 6. 스킬별 자동 품질 게이트

각 스킬을 끝낼 때 다음을 실제 최종 PNG로 검사하고 `PASS`가 아니면 다음 스킬로 넘어가지 않는다.

1. Intent: manifest의 몬스터·스킬명·타입·효과·필수 역할과 일치
2. Identity: GENERATION_SPEC의 핵심 소재가 읽히고 공식 참조의 고유 소재로 대체되지 않음
3. Rendering: 외곽/그림자, 중간톤 면, 국소 코어, 재질 반사와 파편이 분리됨
4. Motion: 준비→성장→절정→해체→fade가 되감기·순간 이동 없이 이어짐
5. Stability: 같은 canvas/pivot/축/공통 스케일이며 프레임별 자동 정렬 흔들림 없음
6. Alpha: 투명 배경, 반투명 가장자리, 흰/검정/회색 matte와 사각 배경 없음
7. Isolation: 몬스터 본체·얼굴·텍스트·번호·UI·다른 스킬 셀 조각 없음
8. Icon: 64px에서 핵심 모티브가 읽히고 VFX와 색·재질·형태 언어 공유
9. Reference: 실제 사용한 보드/원본 경로와 SHA-256 기록, 적용/제외 지시 준수

파일 검사 PASS와 아트 PASS를 따로 기록한다. 모든 프레임의 해시가 같거나, 알파만 달라지고 RGB 형상이 같은 경우 Motion FAIL이다. alpha>0 bbox와 alpha>=16 bbox, 주요 형상 70%와 외곽 85%를 구분한다. 완전히 투명한 바깥 영역이 있어야 하며 알파를 단순 RGBA 변환으로 만들지 않는다. 흰색·검정색·중간 회색 배경에 합성하고 1배율·64px·2배율로 확인한다.

## 7. 진행 상태와 실패 처리

각 스킬이 끝날 때 `WORK_STATE.json`을 갱신한다. 최소 필드는 skill_id, state, attempt, generation method, source path/hash, extracted files, reference board paths/hashes, gate results, unresolved issues다. 상태는 `NOT_STARTED / GENERATING / VALIDATING / PASS / BLOCKED` 중 하나다. 중단되면 마지막 PASS 다음부터 이어간다.

한 스킬의 실패는 Area 전체 이미지를 다시 생성할 이유가 아니다. 실패 원인에 맞게 해당 스킬만 수정한다. 참조가 부족하면 brief의 원본 연속 프레임에서 추가 이미지를 선택하고, 왜 추가했는지 기록한다. 기능이 있는 한 첫 실패에서 멈추지 않는다.

참조 전달에 대한 도구 내부 영수증이 없다는 사유만으로 BLOCKED 처리하지 않는다. 실제 준비 보드 입력과 파일 해시 기록이 있으면 검증 가능한 작업 기록으로 인정한다. 반대로 생성 도구를 호출하지 않았거나 보드를 실제 입력하지 않았다면 완료라고 쓰지 않는다.

## 8. 패키징 전 Area 전체 검증

다섯 스킬이 각각 PASS이고 다음 파일이 실제 존재할 때만 패키징한다.

- VFX {total}장: 8 + 8 + 8 + 12 + 8
- ICON 5장
- 각 VFX는 256×256 RGBA, 연속 번호, 실제 alpha
- 각 ICON은 256×256 RGBA 기본 상태
- 파일명과 폴더는 OUTPUT_NAMING_SPEC와 정확히 일치
- 수정/생성 source, 셀 좌표, 변환, 참조 입력, 해시 기록 존재
- 최종 개별 PNG에서 만든 preview/contact/animation viewer 존재

Preview는 최종 PNG와 제공 MONSTER_IMAGE를 기계적으로 합성한다. Preview 자체를 이미지 생성으로 새로 그리지 않는다. 라벨은 preview에만 허용되며 VFX/ICON 원본에는 금지한다.

`OUTPUT_MANIFEST.csv/.md`, 몬스터별 `RESULT_INFO.md`, `VALIDATION_REPORT.md`, `REFERENCE_INPUTS.json`, `WORK_STATE.json`, `USER_DECISIONS.md`를 작성한다. Markdown 표 안의 `ICON | VFX`는 셀 구분자가 되지 않도록 `ICON + VFX`처럼 기록한다.

ZIP 생성 후 CRC, 엔트리 목록, SHA-256, PNG 수량을 다시 확인한다. 검증된 실제 `AREA_00_IMAGES_OUTPUT.zip`과 전체 preview를 제공한다. 게임 실행은 이번 이미지 제작 범위가 아니므로 `RUNTIME=NOT_CHECKED`라고 기록한다.

## 9. 금지되는 실패형 산출

- 다섯 몬스터가 행으로 배치된 Area 전체 콘셉트 시트
- 단계명·라벨·색 배경과 함께 생성된 VFX
- 몬스터가 공격하는 장면이나 몬스터 얼굴이 있는 ICON
- 마노를 버섯처럼 다른 몬스터로 바꾼 이미지
- 한 장의 생성 이미지를 최종 44프레임처럼 보고한 패키지
- 실패 이미지를 `_FAILED_GENERATION_CANDIDATE`에 넣고 정상 OUTPUT 이름으로 전달
- “참조 입력 UI 감사 불가”만을 이유로 첫 시도 후 전체 중단
- 생성하지 않은 자산을 manifest에서 PASS 처리

이 명령은 AREA 00 전체 신규 제작까지 수행한다. AREA 01 이후는 자동 시작하지 않는다.
'''


def quality_gate_text():
    return '''# AREA 00 제작 품질 게이트

외부 TXT/CHATGPT_IMAGES_MASTER_PROMPT의 단일 스킬 파이프라인을 따른다. 다섯 스킬을 한 이미지에 생성하면 즉시 FAIL이다.

## 스킬별 PASS

- Identity: manifest와 GENERATION_SPEC의 WHAT, 소재, 팔레트, 방향을 유지한다.
- References: 원본 MONSTER_IMAGE와 두 prepared board를 실제 생성 입력으로 사용하고 경로·SHA-256을 기록한다.
- VFX: 요구된 8/12장의 개별 256×256 RGBA PNG가 존재한다.
- Motion: 모든 RGB 형상이 같고 alpha만 달라지는 방식이 아니다. 준비·성장·절정·해체·fade가 실제 형태 변화다.
- Stability: 같은 pivot/축/공통 스케일이며 프레임별 자동 크롭 흔들림이 없다.
- Rendering: 어두운 유색 면, 중간톤, 밝은 코어, 재질별 반사와 통제된 파편이 구분된다.
- Alpha: 바깥쪽에 완전 투명 픽셀이 있고 반투명 가장자리가 있으며 흰/검정/회색 matte가 없다.
- Isolation: 텍스트·번호·UI·몬스터 본체·다른 셀 조각·참조 스킬의 캐릭터/무기가 없다.
- Icon: 256×256 RGBA이며 64px에서 핵심 모티브가 읽히고 완성 VFX와 연결된다.

첫 스킬 001이 이 게이트를 통과하기 전 002~005를 생성하지 않는다. 첫 실패는 원인을 분류해 제작 방식이나 프롬프트를 바꾼 뒤 001만 다시 만든다. 같은 방식의 반복 재시도는 금지한다.

## Area 패키징 PASS

- 정확히 VFX 44장(8+8+8+12+8), ICON 5장
- 연속 번호, 정확한 이름·폴더·canvas·RGBA
- 최종 PNG로 합성한 preview/contact/animation viewer
- manifest/result/validation/reference/state/source·추출 기록
- ZIP CRC와 각 엔트리 SHA-256 확인

하나라도 실패하면 정상 이름 `AREA_00_IMAGES_OUTPUT.zip`을 만들지 않는다. 실패 시안과 보고서만 든 ZIP은 납품물이 아니다.
'''


def readme_text():
    return '''# AREA 00 이미지 신규 제작 — 여기서 시작

사용자는 이 `AREA_00_IMAGES_INPUT.zip`과 옆의 `AREA_00_CHATGPT_PRODUCTION_PROMPT.txt`만 함께 첨부하고 “첨부한 프롬프트대로 실행해줘”라고 요청한다.

`CHATGPT_IMAGES_MASTER_PROMPT.md`는 외부 TXT와 같은 내용이며 최종 실행 절차다. 먼저 001 달팽이 하나로 참조 입력→VFX source→프레임 추출→알파/동작 검증→ICON의 전체 파이프라인을 통과시킨다. 그 뒤 002~005를 한 스킬씩 만든다. 다섯 스킬을 한 이미지에 동시에 생성하지 않는다.

각 몬스터 폴더의 `DESIGN_REFERENCE_BRIEF.md`에는 소재와 참조 원본이 있고, `reference_resource_design/prepared_boards/`에는 생성 호출에 실제 전달할 스킬별 공식 VFX 보드와 AREA00 마감 보드가 있다. 대응 JSON은 각 보드의 원본 이미지 경로·SHA-256·타일 위치를 기록한다.

기존 승인 00은 마감·애니메이션 비교 기준이며 기존 OUTPUT을 덮어쓰지 않는다. 이번 산출은 새 REVIEW_CANDIDATE다. 게임 설정·RUID·AnimationClip·scale·offset은 변경하지 않는다. AREA 01 이후는 자동 시작하지 않는다.
'''


def main():
    with zipfile.ZipFile(ZIP_PATH) as z:
        root = ZIP_PATH.stem + "/"
        data = {n[len(root):]: z.read(n) for n in z.namelist() if n.startswith(root) and not n.endswith("/")}

    rows = list(csv.DictReader(io.StringIO(decode(data["AREA_MANIFEST.csv"]))))
    maps = json.loads(data["reference_resource_design/AREA_REFERENCE_MAP.json"])
    by_skill = {m["skill_id"]: m for m in maps}
    specs = {r["skill_id"]: parse_skill_spec(data, r["folder"]) for r in rows}
    assert [specs[r["skill_id"]]["frames"] for r in rows] == [8, 8, 8, 12, 8]

    backup = COLLECTION / "backups" / f"AREA_00_BEFORE_COMMAND_REBUILD_{STAMP}.zip"
    backup.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(backup, "x", zipfile.ZIP_STORED) as out:
        out.write(ZIP_PATH, ZIP_PATH.name)
        out.write(TXT_PATH, TXT_PATH.name)

    board_report = []
    for row in rows:
        skill_id = row["skill_id"]
        mapping = by_skill[skill_id]
        official_paths = balanced_representatives(mapping["elements"], 16)
        official_entries = [
            {"path": p, "bytes": data[p], "purpose": "official VFX phase reference"} for p in official_paths
        ]
        official_board, official_manifest = contact_board(official_entries)

        finish_paths = list(mapping["area00_full_vfx"])
        if len(finish_paths) > 12:
            indexes = sorted(set(round(i * (len(finish_paths) - 1) / 11) for i in range(12)))
            finish_paths = [finish_paths[i] for i in indexes]
        icon_paths = []
        for element in mapping["elements"]:
            if element["role"] == "icon":
                icon_paths.append(element["source_path"])
        icon_paths.append(mapping["area00_icon"])
        finish_entries = [
            {"path": p, "bytes": data[p], "purpose": "approved AREA00 finish/motion reference"}
            for p in finish_paths
        ] + [
            {"path": p, "bytes": data[p], "purpose": "official or approved icon rendering reference"}
            for p in icon_paths
        ]
        finish_board, finish_manifest = contact_board(finish_entries)

        board_dir = "reference_resource_design/prepared_boards/"
        official_name = board_dir + skill_id + "_OFFICIAL_VFX_BOARD.png"
        finish_name = board_dir + skill_id + "_AREA00_FINISH_BOARD.png"
        manifest_name = board_dir + skill_id + "_BOARD_MANIFEST.json"
        data[official_name] = official_board
        data[finish_name] = finish_board
        board_meta = {
            "skill_id": skill_id,
            "monster_id": row["monster_id"],
            "monster_image": row["folder"] + "/MONSTER_IMAGE.png",
            "monster_image_sha256": sha(data[row["folder"] + "/MONSTER_IMAGE.png"]),
            "official_vfx_board": {"path": official_name, "sha256": sha(official_board), "tiles": official_manifest},
            "area00_finish_board": {"path": finish_name, "sha256": sha(finish_board), "tiles": finish_manifest},
            "board_background": "neutral gray; reference transport only; never copy into OUTPUT",
            "required_generation_inputs": [row["folder"] + "/MONSTER_IMAGE.png", official_name, finish_name],
        }
        data[manifest_name] = json.dumps(board_meta, ensure_ascii=False, indent=2).encode("utf-8")
        board_report.append(board_meta)

        brief_path = row["folder"] + "/DESIGN_REFERENCE_BRIEF.md"
        brief = decode(data[brief_path])
        brief += f'''\n\n## 제작 호출에 바로 사용할 준비 보드\n\n- 실제 몬스터: `{row["folder"]}/MONSTER_IMAGE.png`\n- 공식 VFX 다단계 보드: `{official_name}` / SHA-256 `{sha(official_board)}`\n- 승인 00 마감·ICON 보드: `{finish_name}` / SHA-256 `{sha(finish_board)}`\n- 구성 원본·타일·해시: `{manifest_name}`\n\nVFX 호출에 위 세 이미지를 실제 reference input으로 전달한다. 준비 보드의 회색 배경·격자·참조 고유 형상은 결과에 넣지 않는다. 다섯 스킬을 한 번에 생성하지 않는다.\n'''
        data[brief_path] = brief.encode("utf-8")

    prompt = prompt_text(rows, specs).encode("utf-8")
    data["CHATGPT_IMAGES_MASTER_PROMPT.md"] = prompt
    data["README_START_HERE.md"] = readme_text().encode("utf-8")
    data["QUALITY_GATE.md"] = quality_gate_text().encode("utf-8")
    data["reference_resource_design/prepared_boards/README.md"] = (
        "# Prepared reference boards\n\n"
        "각 스킬의 실제 생성 호출에 전달할 공식 VFX 보드와 승인 AREA00 마감 보드다. "
        "이미지에는 출력물용 라벨을 넣지 않았고 중립 회색 바탕은 참조 보기용이다. "
        "BOARD_MANIFEST.json에 원본 경로·SHA-256·타일 위치가 있다. 원본 파일도 ZIP 안에 유지된다.\n"
    ).encode("utf-8")
    data["COMMAND_SYSTEM_VERSION.json"] = json.dumps(
        {
            "area": "00",
            "version": "single-skill-pipeline-v1",
            "rebuilt_at": STAMP,
            "external_prompt_equals_internal_master": True,
            "skills": 5,
            "required_vfx_frames": 44,
            "required_icons": 5,
            "prepared_board_count": 10,
            "board_manifests": 5,
            "previous_failed_output_is_positive_reference": False,
            "area_wide_generation": "FORBIDDEN",
            "first_skill_gate": "001 must PASS before 002-005",
            "backup": str(backup),
        },
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")

    # Existing PNG/GIF/reference sources/specs stay byte-identical; only new boards and command documents change.
    hashes = []
    for path, blob in sorted(data.items()):
        if path == "INPUT_FILE_HASHES.csv":
            continue
        hashes.append({"path": path, "sha256": sha(blob), "bytes": len(blob)})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=["path", "sha256", "bytes"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(hashes)
    data["INPUT_FILE_HASHES.csv"] = stream.getvalue().encode("utf-8-sig")

    temp = ZIP_PATH.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for path, blob in sorted(data.items()):
            out.writestr(root + path, blob)
    with zipfile.ZipFile(temp) as check:
        assert check.testzip() is None
        assert check.read(root + "CHATGPT_IMAGES_MASTER_PROMPT.md") == prompt
        assert sum(n.endswith("_BOARD.png") for n in check.namelist()) == 10
        assert sum(n.endswith("_BOARD_MANIFEST.json") for n in check.namelist()) == 5
        for row in rows:
            manifest = json.loads(check.read(root + "reference_resource_design/prepared_boards/" + row["skill_id"] + "_BOARD_MANIFEST.json"))
            for item in manifest["required_generation_inputs"]:
                assert root + item in check.namelist()
            for group in (manifest["official_vfx_board"], manifest["area00_finish_board"]):
                assert sha(check.read(root + group["path"])) == group["sha256"]
                for tile in group["tiles"]:
                    assert sha(check.read(root + tile["source_path"])) == tile["source_sha256"]
        for item in hashes:
            assert sha(check.read(root + item["path"])) == item["sha256"]
    temp.replace(ZIP_PATH)
    TXT_PATH.write_bytes(prompt)

    result = {
        "status": "PASS",
        "zip": str(ZIP_PATH),
        "zip_sha256": sha(ZIP_PATH.read_bytes()),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "prompt": str(TXT_PATH),
        "prompt_sha256": sha(prompt),
        "prompt_matches_internal_master": True,
        "skills": len(rows),
        "required_vfx_frames": sum(specs[r["skill_id"]]["frames"] for r in rows),
        "required_icons": len(rows),
        "prepared_boards": 10,
        "backup": str(backup),
        "checks": [
            "ZIP CRC",
            "all board source paths and hashes",
            "all three required generation inputs per skill",
            "external TXT equals internal master",
            "input file hash index",
        ],
    }
    (COLLECTION / "AREA00_COMMAND_SYSTEM_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
