# AREA00 성공 과정 — 확인과 미확인 분리

## 1. 승인 원본 식별
승인 INPUT: D:/maplestory_levup/docs/art/images-input-packages/AREA_00_IMAGES_INPUT.zip

SHA256 d1eb7b7f46061d3ef61c11781f0df0629d407d4415c8464f7567abea3a3dfdf7

승인 OUTPUT: D:/maplestory_levup/docs/art/area00-images-output/AREA_00_IMAGES_OUTPUT_ORIGINAL.zip

SHA256 5271fa0682c4cc76caaf6f4e5627c5fbf3c70ec87fe911b9e5398afb770f6853

이는 BASELINE_INDEX와 기존 검수 SELECTION이 가리키는 검수/승인 대상이다. **실제 최초 생성 호출의 INPUT과 동일했다는 증거는 아니다.** OUTPUT_MANIFEST는 AREA_00_IMAGES_INPUT(2).zip이라고 기록하고 STYLE_ATLAS 미발견이라고 적었다. 기준 INPUT에는 ATLAS가 있으므로 두 입력의 동일성은 UNKNOWN.

## 2. 최초 생성 — 문서 증거만 있는 부분
OUTPUT_MANIFEST는 MONSTER_IMAGE, GENERATION_SPEC, STYLE_INDEX, skills/*/preview를 참고했다고 기록하고, image_gen의 contact/sprite preview 생성→균등분할→요구 규격 PNG 저장, 투명 ICON→256² 정리, Python labeled preview 제작 순서를 설명한다. 그러나 실제 tool call, 개별 참조 목록/순서, 모델 버전, 프롬프트 전문과 원본 알파 처리 코드는 찾지 못했다. 이 설명은 manifest의 자기보고이며 검증된 호출 추적과 구분한다.

보존 CONTACT_PREVIEW가 있다는 이유만으로 이것을 최초 입력 참조라고 단정할 수 없다. 마노2048×1536/4×3시트와512² 프레임 사이 주요 RGB 대응은 refinement 조사에서 확인됐으나 미세알파 차이·인접셀 혼입이 있다. 더 큰 무절단 생성 원본/최초 분할 스크립트는 미확보다. 각 RESULT_INFO는 이름·개수·미리보기만 적고 생성 인자를 기록하지 않았다.

## 3. 반입
AREA_00_IMAGES_IMPORT_REPORT는 이미 완성된 VFX44+ICON5를 원본 픽셀 그대로 업로드했다고 기록하며 재생성/재분할/디자인 변경은 없었다. 반입 과정이 아트를 새로 완성한 것은 아니다. 보고서의 마노 간격100ms와 원래 명세·refinement 뷰어80ms는 다르며 이 진단에서 게임을 조회하거나 수정하지 않았다.

## 4. refinement — 실제 호출/코드로 복원 가능
1. 승인 PNG와 인접 프레임/CONTACT를 검사, 재추출 가능성을 확인. 인접셀 혼입 때문에 독립적 재추출을 최종 채택하지 않음.
2. 마노F05~07 각각512²를768² 투명 작업 캔버스에(128,128)배치.
3. F05 최초 투명 편집 요청은 EDIT_F05 + 검수 F04~07 보드(2장). RGB 체크무늬 출력으로 폐기.
4. 기존 승인 프레임을 검정 위에 합성한 BLACK_F05/06/07을 편집 대상으로 사용. F06은 F05/F07, F05는F06, F07은F06/F08을 시간 참조로 전달. 실제2~3장. MONSTER_IMAGE와 ICON은 이 국소 편집 호출에 없음.
5. 프롬프트는 ONLY clipped boundary repair / preserve composition,palette,central pixels / no redesign. 생성 결과 전체를 채택하지 않고 정합 후 좌우 경계 마스크만 접합.
6. 생성 검정 발광 외곽의 alpha=maxRGB/.97, alpha<3/255 제거, 역합성. 원래 중앙RGBA는 마스크 밖에서 다시 원본 픽셀로 복원. EDIT_RECORDS 3개 모두 core_original_pixels_preserved=true, 정합scale1/dx0/dy0.
7. 고정 중심에서 동일 스킬 전체 공통배율: 이슬.9005(8), 슬라임.8682(8), 마노.7162(12). 총28VFX 변경; ICON5+blue8+red8=21PNG 바이트 보존. PNG_CHANGE_MAP/TRANSFORMS/검증 문서가 이를 기록.
8. 3배경·절단·여백·원본 보존 확인 후 후보 패키징. 재추출 채택0, 원화국소편집3, 크기기술보정28(중복포함).

실제 도움이 된 조건은 이미 완성된 **동일 소재의 편집 대상과 시간 이웃**, 변경 마스크, 원본 중앙알파 보존이었다. 이를 전혀 다른 소재의 신규 생성 성공 레시피로 확대할 수 없다. 검수용 보드 사용도 이 한정된 시간 참조 목적과 신규 스타일 positive 목적을 구분해야 한다.

## 탐색 범위
area00-images-output, area00_refinement/20260912_203404, 관련 output_audit와 현재 세션의 실제 호출을 확인하고 로컬2026/09 세션에서 관련 경로/도구 호출을 검색했다. 원본 생성 로그를 찾지 못한 범위이며, 다른 기기/ChatGPT 대화/삭제된 기록에도 없다는 뜻이 아니다. 증거파일 목록은 evidence/FILE_INVENTORY.csv.
