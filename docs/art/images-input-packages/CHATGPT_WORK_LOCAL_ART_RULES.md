# ChatGPT Work Local — 스킬 아트 공통 실행 규칙

이 문서는 `AREA_XX_CHATGPT_WORK_LOCAL_PROMPT.txt`에서 호출하는 공통 실행 규칙이다. 실제 AREA 작업은 해당 Area의 Work 프롬프트, INPUT ZIP, 외부 제작 프롬프트를 함께 따른다.

## 1. 권위와 충돌 처리

적용 우선순위는 다음과 같다.

1. 각 몬스터 폴더의 `GENERATION_SPEC.md`와 `RUNTIME_ROLE_MAP.md`: 스킬 정체성, 역할, 프레임 수, 캔버스, 타이밍
2. `AREA_MANIFEST.csv/.md`: ID, 이름, 타입, 실제 효과·동작, 처리 순서
3. `DESIGN_REFERENCE_BRIEF.md`: 해당 스킬의 공식 참조와 적용/제외 범위
4. `OUTPUT_NAMING_SPEC.md`, `OUTPUT_FORMAT_SPEC.md`: 파일 구조와 형식
5. Area 외부 제작 프롬프트와 내부 `CHATGPT_IMAGES_MASTER_PROMPT.md`: 실행 절차
6. Area 공통 `QUALITY_GATE.md`: 공통 검사

전역 문서가 모든 VFX를 256×256으로 쓰더라도 스킬별 `GENERATION_SPEC.md`가 512×512 등 다른 캔버스를 요구하면 스킬별 규격이 우선한다. 충돌을 숨기지 말고 `INPUT_CONFLICTS.md`에 기록한다. ICON은 별도 명시가 없으면 256×256 RGBA다.

## 2. 이미지 생성과 참조 전달

- 이미지 원화 생성·편집 단계에서는 ChatGPT Work의 `$imagegen`을 실제로 호출한다.
- 기록 도구명은 `native image generation/editing — version/model unverified`로 쓴다.
- 하나의 생성 호출에는 하나의 monster_id와 하나의 skill_id만 포함한다.
- 각 VFX 호출에 해당 `MONSTER_IMAGE.png`, `*_OFFICIAL_VFX_BOARD.png`, `*_AREA00_FINISH_BOARD.png`를 실제 reference image input으로 연결한다.
- 경로를 문장에 적거나 파일을 열어 본 것만으로 참조 입력 완료라고 기록하지 않는다. 실제 입력한 파일의 절대 경로와 SHA-256을 남긴다.
- MONSTER_IMAGE에서는 색·재질·부위 모티브를 읽되 몬스터 몸·얼굴을 VFX나 ICON에 넣지 않는다.
- OFFICIAL_VFX_BOARD는 명암 구조, 중간톤 분리, 밝은 코어, 반투명 가장자리, 파편 통제, 프레임 전개를 위한 우선 스타일 참조다.
- AREA00_FINISH_BOARD는 알파·가독성·마감 밀도의 기준이다. 그 보드의 다른 스킬 모양과 팔레트를 복제하지 않는다.
- 기존 실패 OUTPUT, 이전 Work 생성 결과, AREA 전체 콘셉트 시트를 positive reference로 사용하지 않는다.

## 3. 원화 도구 제한

Python, Pillow, SVG, Canvas 또는 단순 도형으로 VFX/ICON 원화를 만들지 않는다. 이 도구들은 다음 기계 작업에만 사용할 수 있다.

- 생성 source sheet의 고정 좌표 분리
- 스킬 전체에 동일한 공통 배율·피봇 변환
- 규격 변환과 알파 검사
- Preview 및 animation viewer 합성
- manifest, 검증 문서와 ZIP 제작

생성 결과에 없는 형상을 보간·도형·복제로 채우지 않는다.

## 4. 첫 필수 VFX 앵커

Manifest 순서상 첫 `VFX` 필수 스킬만 먼저 제작한다. 사용자 중간 승인은 요구하지 않되 아래 아트 게이트를 실제 최종 프레임으로 통과해야 다음 스킬로 진행한다.

1. 몬스터·스킬명·타입·실제 효과·방향·역할이 INPUT과 일치
2. 세 참조 이미지가 실제 `$imagegen` 입력으로 전달됨
3. 어두운 유색 외곽/그림자, 분명한 중간톤, 제한된 밝은 코어가 분리됨
4. 공식 참조처럼 재질 두께와 반투명 가장자리가 있으면서 과한 플라스틱·스티커·UI 엠블럼 광택이 없음
5. 준비→성장→절정→해체→fade가 알파 변화만이 아닌 실제 형상 변화로 연결됨
6. 모든 프레임이 스킬별 canvas, 같은 피봇·축·공통 스케일을 유지
7. 텍스트·번호·UI·체커보드·불투명 사각 배경·몬스터 본체·다른 스킬 조각이 없음
8. 흰색·검정색·중간 회색 합성에서 검은 점/대시, 색 잔류, 매트 테두리 같은 오염이 없음
9. ICON은 통과한 VFX와 색·재질·핵심 모티브를 공유하고 64px에서 읽힘

앵커가 실패하면 나머지 스킬을 만들지 않는다. 실패를 `intent/reference/shape/material/motion/alpha/layout/contamination`으로 분류한다. 같은 문구와 같은 생성 방식을 반복하지 말고 원인에 맞게 참조 선택·프롬프트·생성 단위를 바꿔 앵커만 다시 만든다. 실패 이미지는 다른 호출의 참조로 사용하지 않는다.

## 5. 나머지 스킬과 상태 저장

앵커가 통과하면 Manifest 순서대로 한 스킬씩 진행한다. VFX가 필수인 스킬은 VFX 전체가 아트·파일 게이트를 통과한 후 ICON을 만든다. ICON-only 스킬에는 VFX를 임의 생성하지 않는다.

각 스킬 완료 시 `WORK_STATE.json`을 저장한다. 최소 기록은 skill_id, state, attempt, generation method, 최종 source 경로·해시, reference 입력 경로·해시, 추출 좌표, canvas, gate 결과, 미해결 문제다. 중단 시 마지막 PASS 다음부터 재개한다.

## 6. 독립 재검증

제작자가 작성한 PASS 문구만으로 승인하지 않는다. 실제 최종 파일을 다시 열어 다음을 독립 검사한다.

- Manifest와 RUNTIME_ROLE_MAP에 따른 VFX/ICON 필요 수량
- 각 `GENERATION_SPEC.md`에 따른 프레임 수·캔버스·타이밍
- 연속 이름과 폴더 구조
- RGBA, 실제 투명 배경과 반투명 가장자리
- 외곽 픽셀 접촉, 70% 주요 형상과 85% 외곽 안전영역
- 프레임 해시와 RGB 형상 변화
- 같은 피봇·축·공통 스케일 및 자연스러운 전후 연결
- 검은 점/대시, 흰/검정/회색 매트, 인접 셀, 글자, 캐릭터 혼입
- 공식 VFX 참조와의 렌더링 문법 및 게임 자산 가독성
- ICON 64px 가독성과 VFX 연결

아트 게이트와 파일 게이트를 별도로 기록한다. 둘 중 하나라도 FAIL이면 정상 이름의 OUTPUT ZIP을 만들지 않는다.

## 7. 패키징과 종료

모든 필수 스킬이 PASS일 때만 최종 개별 PNG에서 Preview, labeled Preview, contact sheet와 파일 기반 animation viewer를 합성한다. OUTPUT manifest, validation, reference 기록, work state, result info를 포함해 해당 Area의 `AREA_XX_IMAGES_OUTPUT.zip`을 만든다.

ZIP 생성 후 CRC, 엔트리 목록, SHA-256, 필수 PNG 수량을 다시 확인한다. 게임 실행은 수행하지 않고 `RUNTIME=NOT_CHECKED`로 기록한다. 해당 Area의 ZIP을 만든 뒤 멈추고 다음 Area를 자동 시작하지 않는다.
