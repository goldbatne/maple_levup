> **추가 전체 스타일 검수:** 기존 포괄적 스타일 평가는 [CROSS_AREA_STYLE_SUMMARY.md](CROSS_AREA_STYLE_SUMMARY.md) 및 CROSS_AREA_STYLE_REVIEW.csv로 대체합니다. 검사 대상 209역할 중 유지 가능 162, 스타일 이탈 37, 사용자 판단 10. 기존 명세 판정과 AREA11 투명도 기술 보류는 별도 유지합니다.

# MSW 원본 ↔ 몬스터 스킬 아트 적합성 검수

실행 폴더: `D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review`  
보고서 작성: 2026-09-12T16:51:53 (로컬 KST)

## 결론

**19개 Area / 99개 몬스터·스킬 / 209개 역할 / 실제 납품 PNG 933개**를 확인했다. 원화 수정 후보는 **AREA 11 킹 블록퍼스의 PROJECTILE 4장**이다. 이전 보고의 **킹 블록퍼스 CAST와 장난감 목마 CAST 보류 판단은 실제 프레임에서 근거가 재현되지 않아 정정**한다. 원화·ZIP·INPUT·게임 데이터에는 손대지 않았다.

| 집계 단위 | NO_OBVIOUS_ISSUE | SPEC_MISMATCH | STYLE_OUTLIER | NEEDS_USER_REVIEW | NOT_CHECKED |
|---|---:|---:|---:|---:|---:|
| 설정·소재·동작 적합성: 역할 | 208 | 1 | 0 | 0 | 0 |
| 설정 적합성: 몬스터·스킬 쌍 | 98 | 1 | 0 | 0 | 0 |
| 스타일: 역할 | 209 | 0 | 0 | 0 | 0 |

역할 구성은 ICON 99, CAST_VFX 63, PROJECTILE 12, REFERENCE_VFX 35다. 수정 후보 1역할의 사용자 선택은 ‘현행 명세대로 후속 수정’ 또는 ‘기존 본체형 탄을 유지하기 위한 명시적 예외 승인’이다. 두 조치를 별개 오류로 중복 집계하지 않았다. **NO_OBVIOUS_ISSUE는 사용자 최종 승인이나 런타임 성공이 아니다. USER_APPROVED는 기록하지 않았다.**

## 대상과 기준 선택

- 실제 대상 Area: 01, 02, 03, 04, 05, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20. AREA 06은 AUDIT_RULES의 예약 결번이며 AreaTable과 승인 INPUT 목록에도 없다. AREA 00은 기준 아트로만 사용했다.
- 19개 INPUT은 BASELINE_INDEX의 승인 V2.4 경로와 SHA256으로 고정했다. AREA00 승인 INPUT/OUTPUT/리소스맵/반입 보고서와 V2.4 검증자료를 포함한 기준·완료 OUTPUT **41개 해시가 모두 일치**했다.
- 17개 OUTPUT은 `output_repacked/20260912_153221_v24_repack`의 BASELINE_OUTPUT_INDEX 일치 ZIP이다. AREA11/12는 `output` 폴더의 후보 ZIP을 해시로 비교하여 기존 CONTENT_STYLE의 REUSED_FILE_CHECKS와 일치하는 단일 파일을 각각 선택했다. 파일시각·접미사로 고르지 않았다. VERSION_CONFLICT 0건.
- Area별 INPUT 버전·경로·해시, OUTPUT 경로·해시, 선택 근거는 [AREA_SELECTION.csv](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/AREA_SELECTION.csv)에 있다. 원본 OUTPUT 후보 해시 전부는 ORIGINAL_OUTPUT_HASHES.csv에 기록했다.

## 실제 MSW 원본 확인

| 확인 수준 | 몬스터 수 |
|---|---:|
| MSW_ORIGINAL_CONFIRMED | 99 |
| CACHED_SOURCE_CONFIRMED | 0 |
| INPUT_ONLY | 0 |
| SOURCE_UNVERIFIED | 0 |

연결 Maker의 실제 읽기 전용 `maker_get_world_info` 응답은 worldId `6ab29f6a728e4b33931679be708ca6b1`이다. 그 호출은 연결 식별만 증명한다. 모델 구성은 로컬 MonsterTable → ModelBuilder 읽기 전용 snapshot으로 확인했고, 원본 그림은 msw-search의 검증된 공식 조회 경로에서 **정확한 RUID 99개를 배치 조회**해 반환된 공식 Nexon CDN GIF를 직접 내려받았다. 없는 Maker API나 원격 엔티티 조회 결과를 가정하지 않았다.

99개 모두 animationclip이다. 모델 SpriteRUID와 INPUT RUID가 일치하고, 공식 메타데이터의 프레임 수와 실제 GIF 프레임 수가 모두 맞는다. 조회 이미지의 실루엣·색·얼굴/장비를 INPUT과 직접 대조했다. 전체 GIF 프레임 접촉시트에 더해 9프레임 이상 21개 원본은 첫·중간·마지막 프레임 확대 자료 5장을 확인했다. 대상 모델의 자식 구성요소는 모두 0개였으며 ActionSheet의 stand/move/attack/hit/die 연결도 기록했다. 정체성 확인에 사용한 SpriteRUID 외 모든 동작 clip의 별도 다운로드나 게임 렌더링 검사는 하지 않았다.

이전 V2.1 원본 증빙은 모델 RUID/패키지 해시를 기록했지만 원본 다운로드·프레임 증빙을 충분히 제공하지 않아 캐시 확인 완료로 올리지 않았다. 이번에 99개 모두 실제 조회했다. 성공한 동일 RUID를 불필요하게 반복 조회하지 않았다. 공식 API는 불변 리소스 revision을 제공하지 않으므로 **조회시각+응답 메타데이터+반환 이미지 SHA256 스냅샷**을 버전 근거의 한계로 기록했다. 공식 GIF는 실제 리소스의 thumbnail 표현이며 native texture 원본 파일이나 실행 화면의 픽셀 동일성을 뜻하지 않는다.

근거: [SOURCE_CHECK.csv](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/SOURCE_CHECK.csv), resource_batch_*.json, resource_metadata.json, download_log.json, model_snapshots.json, source_copies/*.gif, boards/area_*_source_and_all_frames.png, boards/source_detail_*.png.

## 확정 스킬·프로젝트 데이터 대조

MonsterTable의 몬스터명·레벨·모델·drop_skill_id와 INPUT 연결 99건이 맞고, RoomTable에 각 INPUT Area와 일치하는 해당 몬스터 배치가 있다. 승인 사본으로 해결된 V2.1 evidence의 `current_candidates/Mislocated_SkillTable.csv`와 현행 `Mislocated/MyDesk/GameData/SkillTable.csv`는 대상 99행의 전체 필드가 일치한다. 스킬명도 INPUT과 일치한다. 과거 baseline_commit의 SkillTable은 다른 후보로 구분했으며 현재 파일을 임의 수정하지 않았다.

다만 정식 RootDesk의 SkillTable.csv/.userdataset 부재로 Maker 등록 상태는 확정할 수 없다. **승인 후보와 현재 후보가 같다는 사실을 ‘현재 등록 데이터가 정상’으로 바꾸어 기록하지 않았다.**

19개 AREA_MANIFEST, FULL_ART_SCOPE, OUTPUT_REQUIREMENTS, ASSET_BINDING_PLAN과 99개 GENERATION_SPEC/RUNTIME_ROLE_MAP을 연결해 209개 실제 역할의 계약을 저장했다. 요구 역할/제작 결정/프레임 수의 계약 연결이 맞는다. 각 역할의 소재·허용 기호·금지 본체·방향·엔진 이동·시간 흐름을 실제 납품 PNG 전체와 대조했다. REFERENCE를 실제 CAST/지속 버프로 간주하지 않았고, ICON의 얼굴 모티브 허용을 CAST로 확대하지 않았다. 시트는 시간 순서·방향 판단 근거이며 프레임 속도의 게임 내 체감·판정 성공 검증은 아니다.

근거: [ART_REVIEW.csv](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/ART_REVIEW.csv) (209행), CONTRACT_SNAPSHOTS.json, PROJECT_DATA_CHECK.csv. 기존 관찰 기록은 보조로 재사용하되 실제 전체 프레임을 다시 열었고, 오류가 드러난 King/Toy 서술은 새 관찰로 교체했다.

## AREA 11·12 재판정

### AREA 11 — 킹 블록퍼스 / 왕관 블록탄

| 역할 | 이번 판단 | 실제 관찰과 조치 |
|---|---|---|
| CAST_VFX (8장) | NO_OBVIOUS_ISSUE | F01~F03은 눈·포구 없는 왕관/입방체 조립, F04 섬광, F05 오른쪽 발사, F06~F07 잔광이다. 현재 CAST 계약에 맞는다. **원화 유지.** |
| PROJECTILE (4장) | SPEC_MISMATCH | F00~F03에 원본과 같은 분홍 사각 몸통·검은 눈·원형 포구·왕관 조합이 반복된다. 촉수가 없어도 얼굴/몸통이 있는 축소 개체로 읽혀 VFX의 몸·얼굴 금지와 충돌한다. **이 역할만 원화 수정 후보.** |
| ICON (1장) | NO_OBVIOUS_ISSUE | 왕관 블록과 각진 탄 궤적이라는 UI 모티브에 맞는다. **원화 유지.** |

왕관·각진 블록·에너지 조각 자체는 허용한다. 이를 삭제하라는 요청이 아니다. PROJECTILE에 남은 원본 얼굴·몸통의 결합이 문제다. 기존 보고가 PROJECTILE의 본체 판단을 CAST까지 넓힌 부분은 철회한다. 원화를 유지하려는 경우에만 명시적 예외 승인이 필요하며 이번 검수는 승인하지 않았다.

비교: [AREA11 판정 이미지](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/evidence/area_11_m_king_bloctopus_ruling.png).

### AREA 12 — 장난감 목마 / 태엽 목마 돌진

**CAST_VFX와 ICON 모두 NO_OBVIOUS_ISSUE. 기존 아트 보류 판단을 정정한다.** CAST F00~F03을 384px 원본으로 확대하면 금색 이중 고리는 태엽 구멍, 갈색 동심원은 바퀴/축으로 읽힌다. 주변의 곡선 나무편에는 눈·귀·주둥이를 갖춘 목마 머리나 상체가 확인되지 않는다. F04~F07은 짧은 속도선·나무 파편·별 입자의 소멸이며, 전체 목마가 출발점부터 도착점까지 달리는 반복도 아니다. ‘바퀴·태엽 + 도착점 충돌’ 계약과 부합한다.

ICON에는 눈 달린 목마 머리가 실제로 있으며, 이것은 ICON 조항에 명시적으로 허용된 모티브다. **CAST에 얼굴이 있다는 이전 전제가 실제 그림에서 재현되지 않았으므로, 그 전제에 근거한 수정이나 사용자 예외 승인도 요구하지 않는다.** 이것은 ICON 허용을 CAST로 확대 해석한 결론이 아니다.

비교: [AREA12 판정 이미지](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/evidence/area_12_m_toy_trojan_ruling.png), [F00·F02·F03 원본 크기 상세](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/evidence/toy_cast_00_02_03_detail.png), [F01 원본](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/evidence/toy_cast_F01_original.png).

## 스타일와 Preview

AREA00 승인 실제 ICON/VFX의 재질 경계·중간톤·밝은 코어·반투명 잔광·입자 해체를 기준으로 전 대상의 실제 납품 프레임을 비교했다. 같은 역할의 일반/보스 크기 차이와 지역 팔레트 차이를 허용했으며 **명백한 스타일 이탈은 0건**이다. 작은 ICON은 64px 표시에서도 대표 실루엣과 보조 효과를 확인했다. 킹 블록퍼스 PROJECTILE의 문제는 마감 방식이 아니라 소재/금지 조건 충돌이다.

MSW 스타일 라이브러리는 실제 내용도 열었다. 16개 표본 중 명확한 별형 충격·빛고리·먹물·전격·불꽃을 보여주는 7개를 보조 비교에 사용했다. 흰 배경과 희미한 잔상만 보이는 나머지 9개 표본은 이번 마감 비교의 근거에서 제외했다. 이름이 몬스터명이어도 실제 그림이 이펙트인 경우만 사용했다. MONSTER_CHARACTER/EXCLUDE_STYLE와 빈 썸네일을 VFX 근거로 사용하지 않았다. 출시·개정 시기가 미확인된 자료를 최신 공식 스타일이라고 주장하지 않는다. 형성·해체의 시간 표현은 특히 AREA00 및 실제 납품 전 프레임을 기준으로 보았다.

실제 OUTPUT의 19개 Area overview도 직접 열어 몬스터 원본/ICON/납품 프레임 대응을 확인했다. **AREA11 overview는 역할 라벨과 몬스터명·설명이 겹친다.** 원화 불일치와 별개인 기술 보정 항목이다. AREA09의 이전 글꼴 문제를 새 원화 오류로 이월하지 않았다. Preview는 판정의 대체물이 아니며, 전수 OCR/모든 내장 픽셀의 원본 동일성 검사까지 수행했다고 주장하지 않는다. 기존 labeled preview 경로 검사는 해시가 같은 기술 검사 기록을 재사용했다.

근거: STYLE_REFERENCE_CHECK.csv, PREVIEW_CHECK.csv, boards/style_reference_candidates.png, boards/area00_approved_actual.png, boards/preview_review_01..05.png, [AREA11 Preview 문구 겹침](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/evidence/area_11_overview_top_detail.png).

## 기존 검사 재사용과 남은 별도 항목

- AUDIT_RULES와 BASELINE_INDEX 해시가 이전 content_style 기록과 일치한다. 17개 REPACK의 839개 역할 PNG는 현재 읽은 바이트 해시가 이전 보존 기록의 원본/납품 SHA256과 모두 같다. CRC·경로·규격·알파 검사와 Area00 원화 보존 검사는 해당 동일 대상의 기존 결과를 재사용했다. 이번에 전체 ZIP 검사나 REPACK을 재실행하지 않았다.
- AREA11/12 원본의 기술 보정은 아직 남는다. AREA11 manifest의 canonical per-file 열 누락 및 대소문자/폴더명에 따른 기대 경로 불일치, AREA12 manifest의 canvas/relative_path/sha256 누락과 일부 폴더 공백/밑줄 차이를 이전 같은 해시의 기록에서 유지했다. **실제 원화가 없다는 뜻은 아니다.** 이번에 해당 PNG와 preview를 다른 실제 경로에서 찾아 확인했다. 상세는 HELD_TECHNICAL_ITEMS_REUSED.csv다.
- 이전 지역 검토 중 **킹크랑은 AreaTable.note에 ‘플로리나 비치에서 건너온 킹크랑’이 명시되어 있어 프로젝트의 의도적 배치 근거가 있다.** 별도 사용자 배치 승인을 반복 요구하지 않는다. 스톤골렘·버블링은 프로젝트 배치와 INPUT이 일치하되 재배치 서사의 확인사항만 남긴다. ‘발굴지의 석면’은 돌의 면/가면을 뜻하는 창작 명칭인지 기획 확인으로 남긴다. 세 항목 모두 아트 불합격·재생성 사유가 아니다. 이전 외부 지역/명칭 기록은 기획 질문의 출처로만 인용하며 이번에 새로 외부 사실을 검증했다고 주장하지 않는다.
- SkillTable 등록, DEF 패시브, 돌진 CAST 부착점은 아트와 별도 런타임 미확인 사항이다. Maker 실행·refresh·play·입력·게임 반입은 하지 않았다.

## 다음 단계 인계

원화 관점에서 **98개 쌍 전체 + 킹 블록퍼스 CAST/ICON, 합계 208개 역할(929 PNG)**을 유지 대상으로 넘길 수 있다. **기술 보정 완료 상태까지 포함한 기존 인계 대상은 17개 Area / 89개 쌍**이다. AREA12의 5개 쌍과 AREA11의 나머지 정상 아트도 유지하되 패키지 기술 보정은 별도 후속 작업이다. AREA11 PROJECTILE 1역할만 수정/예외 승인 결정 대상으로 남는다.

조치 목록: [ACTION_ITEMS.csv](D:/maplestory_levup/docs/art/output_audit/runs/20260912_162508_msw_origin_art_review/ACTION_ITEMS.csv). 수정·기술 보정·기획 질문·선택적 예외 승인을 구분했고 이번에는 어느 조치도 실행하지 않았다. 생성 이력 부재만으로 재생성을 요구한 항목은 없다.

## 증빙 파일

- 주요 결과: REVIEW_SUMMARY.md, SOURCE_CHECK.csv, ART_REVIEW.csv, ACTION_ITEMS.csv.
- 기준/무결성: AREA_SELECTION.csv, BASELINE_HASH_CHECK.csv, ORIGINAL_OUTPUT_HASHES.csv, REUSE_PNG_CHECK.csv, EVIDENCE_INDEX.csv.
- 데이터/조회: PROJECT_DATA_CHECK.csv, CONTRACT_SNAPSHOTS.json, model_snapshots.json, resource_batch_*.json, resource_metadata.json, download_log.json, MCP_READ_ONLY_OBSERVATION.json.
- 직접 시각 대조: boards/ 전체, evidence/ 판정/확대/Preview 비교 이미지, source_copies/ 공식 GIF 사본.

이미지는 기존 원본과 납품 파일의 기계적 배치·확대·문구 합성뿐이다. 새 몬스터나 새 스킬 아트는 그리지 않았다. 모든 새 파일은 이 감사 실행 폴더 안에만 저장했다.
