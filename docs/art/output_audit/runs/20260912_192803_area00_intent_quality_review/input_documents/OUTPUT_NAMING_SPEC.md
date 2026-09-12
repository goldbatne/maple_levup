# Output Naming Spec

출력 루트: `AREA_00_IMAGES_INPUT_IMAGES_OUTPUT/`

## 필수 주 납품물

- VFX는 반드시 프레임 분리형 개별 RGBA PNG로 납품한다.
- 이름: `NNN_[monster_id]_[skill_id]_F00.png`, `F01.png`, `F02.png` ...
- `F00`부터 GENERATION_SPEC의 마지막 프레임까지 번호를 끊거나 건너뛰지 않는다.
- 아이콘: `NNN_[monster_id]_[skill_id]_ICON.png`
- NNN은 AREA_MANIFEST의 작업 순번 3자리다.
- monster_id와 skill_id를 축약하거나 번역하지 않는다.

## 선택적 미리보기

- contact sheet 또는 sprite sheet는 검수 편의를 위한 선택적 preview만 허용한다.
- 선택 파일명: `NNN_[monster_id]_[skill_id]_CONTACT_PREVIEW.png`
- sheet는 주 납품물이 아니며 개별 `F00...` 파일을 대체할 수 없다.

```text
AREA_00_IMAGES_INPUT_IMAGES_OUTPUT/
├─ OUTPUT_MANIFEST.md
├─ OUTPUT_MANIFEST.csv
└─ monsters/
   ├─ 001_[monster_id]_[name]/
   │  ├─ VFX/
   │  │  ├─ 001_[monster_id]_[skill_id]_F00.png
   │  │  ├─ 001_[monster_id]_[skill_id]_F01.png
   │  │  └─ ...
   │  ├─ ICON/
   │  │  └─ 001_[monster_id]_[skill_id]_ICON.png
   │  ├─ PREVIEW/  # 선택 사항
   │  └─ RESULT_INFO.md
   └─ ...
```
