# AREA00 / AREA01 제작 차이 진단

**확인된 것은 단일 원인이 아니라 실행별 원인이 달랐다는 점이다. AREA00 최초 생성의 정확한 성공 레시피는 현재 증거로 복원할 수 없다.** 그 빈칸을 refinement 방식으로 대신 설명한 것이 이후 생산 판단의 큰 오류다.

## 결론과 증거 수준
|분류|판정|범위와 증거|
|WRONG_REFERENCE_PRIORITY|확인된 생산 설계 오류|최초 VFX에 새 ICON을 함께 전달하고 같은 ICON 마감을 요구(L522). 일반 배치 jobs.py는 VFX/ICON 구분 없이 마노 ICON을 고정 사용. 이후 앵커는 VFX 참조로 교정됐지만 여전히 포자 소재/동작의 시각 기준은 확보되지 않았음.|
|ICON_REFERENCE_DOMINANCE|최초 실패의 가장 유력한 스타일 원인, 인과 크기는 추론|최초 주황 버섯 ICON과 후속 CAST의 굵은 금갈색 윤곽·물방울 같은 연두·꽃 같은 덩어리가 원화부터 공통. 실제 ICON 참조와 'same professional finish as icon' 지시 확인. 통제 실험이 없으므로 모델 내부 지배력 확정은 불가.|
|PROMPT_DRIFT|확인|ANCHOR 두 번째 프롬프트가 포자 점/구름을 'pointed comma-like powder wisps', 'ivory highlight ridges'로 구체화(L1269). 출력의 장식적 세 갈래는 단순 배경 오류 이전부터 존재. 금빛/꽃잎 실패 후 금지어만 늘리는 방식으로 검증된 포자 형태 대신 새로운 외형 묘사를 계속 추가.|
|GENERATION_SPEC_MISINTERPRETATION|부분 확인|스킬 ID/역할은 유지했으나 점 입자를 물방울·광택 덩어리로 해석하고, 앵커 시도2에서는 MONSTER_IMAGE 입력까지 빠짐. 전체8프레임이 없는 이후 실행은 리듬 성공을 검사할 수 없음.|
|TRANSPARENCY_PIPELINE_DAMAGE / POSTPROCESS_DAMAGE|직접 확인된 독립 원인|RGB 검정 원본 전체에 밝기 기반 알파 적용, 이후 파랑/분홍 원본에 고정 전경색 비율 가정 적용. 분홍 원본의 크림색이 실제 계산으로 녹색 우세로 변함. ALPHA_NUMERIC.json.|
|REFERENCE_CONTAMINATION|최초 내부 ICON 연결은 확인, 이후 기존 OUTPUT 오염은 발견 안 됨|최초 주황 버섯 CAST는 그 실행에서 방금 만든 ICON(나중에 실패 판정)을 positive 사용. RESTART/ANCHOR/GRAMMAR 새 원화에는 기존 AREA01 OUTPUT/실패본 경로 없음. ANCHOR 알파 시험만 실패본을 편집 대상으로 사용했으며 스타일 positive 아님.|
|IMAGE_TOOL_OR_MODEL_DIFFERENCE|UNKNOWN|AREA00 원본 문서는 image_gen이라고만 기록. refinement와 AREA01 실제 호출은 같은 built-in image_gen__imagegen. 숨겨진 모델 버전/투명 지원 차이는 확인 불가. 같은 도구에서도 최초 ICON은 실제 RGBA, CAST는 RGB였음.|
|UNKNOWN|명확히 남김|AREA00 최초 실제 생성 INPUT 해시, 개별 참조 이미지 목록·순서, 모델/모드, 원본 알파 분리 코드와 정확한 원시 시트 계보.|

## 기존 AREA01 OUTPUT 오염 여부
주황 버섯 최초 CAST에는 현재 실행에서 새로 만든 ICON이 **실제로** 들어갔다. 재시작 이후에도 기존 실패 OUTPUT이 몰래 반복 입력됐다는 증거는 없다. 최초 머쉬맘 재시도 L647에는 현재 AREA01 OUTPUT/SOURCE_SHEET 아래 ICON 경로를 넣으려는 호출이 있었으나 경로 접근 성공/채택은 별도이며 주황 버섯 앵커가 아니다. 이를 전체 실행에 일반화하면 잘못된 결론이다.

현재 디렉터리에 실패본이 남아 있는 것과 자동 selector가 이를 고른 것은 다르다. 확인한 jobs.py는 현재 Area OUTPUT 검색 우선이 아니라 **고정 AREA00 마노 ICON**을 선택했다. 파일 이름 source_00_1/2도 각각 동일 SHA로 확인돼, 별도 생성 2회로 세면 안 된다.

## 가장 큰 차이
AREA00 refinement는 이미 원하는 재질·형태·시간 흐름·알파를 가진 기존 그림을 국소 수리했다. AREA01은 다른 소재를 새로 생성하면서 정지 참조 몇 장과 언어 묘사에 의존했고 알파도 새로 추정했다. 이는 성공한 최초 생성 방식을 재현한 것이 아니다. 최초 AREA00 원화의 생성 인과는 UNKNOWN이다.

다음 작업 전에는 ICON→VFX 참조 연결 및 재질을 장식으로 유도하는 추가 묘사를 제거하고, 전체 프레임의 형태 목표와 소재 보존 가능한 알파 경로를 각각 검증해야 한다. 새 생성은 이번 진단에서 수행하지 않았다.

근거: [실제 호출](TOOL_INPUT_TRACE.md), [참조 경로·해시](REFERENCE_TRACE.csv), [알파 분석](ALPHA_PIPELINE_ANALYSIS.md), [재개 제안](NEXT_PRODUCTION_PLAN.md).
