# ChatGPT Work Local — 스킬 아트 공통 실행 규칙 V2

이 문서는 AREA 07~20 재실행에 사용하는 공통 규칙이다. 기존 실행 폴더와 기존 `CHATGPT_WORK_LOCAL_ART_RULES.md`는 과거 실행 근거이므로 수정하지 않는다.

## 1. 기준과 참조

적용 우선순위는 다음과 같다.

1. 각 몬스터의 `GENERATION_SPEC.md`, `RUNTIME_ROLE_MAP.md`
2. `AREA_MANIFEST.csv/.md`
3. `DESIGN_REFERENCE_BRIEF.md`
4. `OUTPUT_NAMING_SPEC.md`, `OUTPUT_FORMAT_SPEC.md`
5. Area 제작 프롬프트와 `CHATGPT_IMAGES_MASTER_PROMPT.md`
6. `QUALITY_GATE.md`

각 생성 호출에는 하나의 monster_id와 하나의 skill_id만 넣는다. 해당 `MONSTER_IMAGE.png`, `*_OFFICIAL_VFX_BOARD.png`, `*_AREA00_FINISH_BOARD.png`를 실제 reference image input으로 전달하고 절대 경로와 SHA-256을 기록한다. 실패본과 다른 Area 결과는 positive reference로 사용하지 않는다.

## 2. 배치 공통 알파 사전 검사

여러 Area가 각자 다른 알파 처리법을 만들지 않도록 이미지 생성은 한 번에 한 작업선만 실행한다. INPUT 해시 계산과 문서 확인은 병렬로 해도 되지만 `$imagegen` 호출은 직렬로 수행한다.

배치의 첫 VFX 앵커에서 다음을 한 번만 결정한다.

1. 투명 배경을 명시해 직접 RGBA source를 최대 2회 생성한다.
2. 저장된 실제 PNG의 mode와 alpha extrema를 검사한다.
3. 직접 RGBA가 정상이면 배치 전체에 `DIRECT_RGBA` 방식을 사용한다.
4. RGB 체커보드 또는 불투명 RGB가 반복되면 그 결과를 폐기하고 `SOLID_MATTE_RECOVERY` 방식으로 전환한다.
5. 같은 직접 투명 요청을 Area마다 반복하지 않는다.

체커보드가 RGB에 구워진 이미지는 알파 복구 원본으로 사용하지 않는다.

## 3. 허용되는 SOLID_MATTE_RECOVERY

직접 RGBA가 실패한 경우에만 다음 복구를 허용한다.

- `$imagegen`으로 그림을 만들 때 체크무늬가 아닌 단일 균일 매트 색을 명시한다.
- VFX에는 소재와 충돌하지 않는 단색 크로마 매트를 우선 사용한다. 밝은 발광의 색 보존이 더 좋은 경우 균일 검정 매트를 사용할 수 있다.
- ICON에는 어두운 외곽선을 보존할 수 있도록 소재와 겹치지 않는 단색 크로마 매트를 사용한다.
- Python/Pillow는 고정 좌표 분리, 공통 배율·피봇, 매트→알파 변환, 가장자리 색 번짐 제거, 리샘플, 검사, Preview와 ZIP 제작에만 사용한다.
- 새로운 선, 파편, 발광, 형상 또는 중간 프레임을 계산·도형·복제로 만들지 않는다.
- 사용한 매트 RGB, 임계값, 알파 계산법, 공통 배율, 피봇, 추출 좌표를 기록한다.
- 기록의 generation method는 `native image generation/editing — version/model unverified + mechanical alpha recovery from uniform solid matte`로 쓴다.

한 매트 색에서 가장자리 오염 또는 핵심 색 손실이 생기면 같은 방법을 반복하지 않는다. 소재와 겹치지 않는 다른 매트 색으로 1회만 다시 생성한다. 두 매트 모두 실패하면 해당 앵커를 BLOCKED로 둔다.

## 4. 앵커와 아트 게이트

Manifest 순서상 첫 VFX 필수 스킬을 먼저 완성한다. 다음 조건을 모두 통과하기 전에는 나머지 스킬을 만들지 않는다.

1. 몬스터·스킬명·타입·효과·방향·역할이 INPUT과 일치한다.
2. 세 참조 이미지가 실제 `$imagegen` 입력으로 전달됐다.
3. 어두운 유색 외곽/그림자, 명확한 중간톤, 제한된 밝은 코어가 분리된다.
4. 공식 참조와 AREA 00처럼 재질 두께와 반투명 가장자리가 있고, 플라스틱 스티커나 UI 엠블럼처럼 보이지 않는다.
5. 준비→성장→절정→해체→fade가 실제 형상 변화로 이어진다.
6. 동일 canvas, 피봇, 기준축, 공통 스케일을 유지한다.
7. 텍스트·번호·UI·체커보드·불투명 사각 배경·몬스터 본체·다른 셀 조각이 없다.
8. ICON은 VFX와 색·재질·핵심 모티브를 공유하고 64px에서 읽힌다.

## 5. 알파 및 오염 게이트

최종 개별 PNG를 직접 검사한다.

- PNG mode가 RGBA이고 alpha에 0, 1~254, 255가 실제로 존재한다.
- alpha>=16의 형상이 스킬별 안전영역을 지킨다.
- 외곽 픽셀의 alpha>=16 접촉이 없다.
- 흰색·검정색·중간 회색 배경 합성에서 매트 테두리, 키 색 잔류, 검은 점/대시, 잘린 광택이 없다.
- 원본 solid-matte source와 최종 합성본의 형상·색·프레임 순서를 나란히 비교한다.
- 크로마 제거 때문에 의도한 녹색/청록/자홍 계열 소재가 비거나 어두운 외곽이 깎이면 FAIL이다.
- 검정 매트 복구에서 어두운 유색 외곽과 연기층이 사라지면 FAIL이다.

`DIRECT_RGBA`와 `SOLID_MATTE_RECOVERY`는 모두 최종 파일 게이트를 통과해야 한다. 복구 방식을 숨기거나 직접 RGBA라고 기록하지 않는다.

## 6. 작업 순서와 상태

한 채팅에서 여러 Area를 처리해도 이미지 생성은 Area 순서대로 진행한다. 각 Area는 앵커 PASS 후 나머지 스킬을 하나씩 완성한다. 한 Area가 BLOCKED면 기록하고 다음 Area로 넘어갈 수 있다.

각 스킬의 `WORK_STATE.json`에는 reference 경로·해시, source 경로·해시, alpha mode, 추출/변환 기록, canvas, gate 결과와 미해결 문제를 저장한다. 이전 실행의 PASS 문구를 재사용하지 않고 실제 최종 PNG를 독립 재검증한다.

모든 필수 스킬이 아트·파일 게이트를 통과한 Area만 정상 이름의 OUTPUT ZIP을 만든다. ZIP 생성 후 CRC, 엔트리, SHA-256, PNG 수량을 확인한다. 게임 실행은 하지 않고 `RUNTIME=NOT_CHECKED`로 기록한다.
