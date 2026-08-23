# 몬스터 스킬 아이콘 원본 (T20-6)

몬스터 스킬 5종의 아이콘을 **직접 그렸다.** 여기 있는 것이 그 원본이다 —
고치고 싶으면 여기서 고쳐 다시 찍고 올린다.

## 왜 그렸나

원작에는 **몬스터 스킬 아이콘이라는 것 자체가 없다.** 몬스터는 스킬을 쓰지만
아이콘을 갖지 않는다. 그래서 쓸 수 있는 재료가 넷뿐이었고 셋은 시도해 탈락했다:

| 계열 | 판정 |
|---|---|
| 원작 플레이어 스킬 아이콘 (T20-1) | ❌ 사람이 쓰는 기술로 읽힌다 |
| 몬스터 카드 (T20-4) | ❌ 넷이 전부 같은 빨간 액자라 아이콘 크기에서 구분이 안 된다 |
| 몬스터 드랍 부위 (T20-5) | △ 모양·색은 갈리지만 **재료 아이템처럼 보인다** |
| **직접 그리기 (T20-6)** | ✅ 무엇을 하는 스킬인지 그림이 말한다 |

대표 판정: *"저런 형식으로 가자 기존 메이플스토리의 스킬과 같이 별다를게 없네"*

## 규칙

- **논리 격자 28×28, 출력 56×56** (한 칸 = 2px). 게임의 아이콘 칸이 정확히
  56px이라 **확대·축소가 한 번도 안 일어난다** — 픽셀이 뭉개지지 않는다.
  그래서 `SkillTable.icon_ratio`는 5종 전부 `1.00`이다.
- **판(plate)은 5장이 완전히 같다.** `draw-icons.cjs`의 `PLATE` 한 곳에서 찍는다.
  원작 스킬 아이콘과 같은 틀이라 스킬 창에서 "재료"가 아니라 "스킬"로 읽힌다.
- **각 스킬은 색이 겹치지 않는다** — 청록 / 파랑 / 주황+초록 / 베이지+노랑 / 회색.
  격자에서 이름을 안 읽어도 갈린다.
- 안티에일리어싱 없음, 그라데이션 없음 (chunky 규칙).

## 고치는 방법

```bash
node docs/art/skill-icons/draw-icons.cjs
python docs/art/skill-icons/rasterize.py docs/art/skill-icons/skill-spore-spray.svg out.png 2
```

`rasterize.py`가 `<rect>`만 읽어 그대로 픽셀로 찍는다.
`msw-painter`의 `render.cjs`(puppeteer)를 안 쓰는 이유는 스킬 폴더에
`package-lock.json`이 없어 `npm ci`가 실패하기 때문이다. 이 그림은 사각형만
쓰므로 결과는 같다.

찍은 PNG는 `msw-mcp`의 `asset_create_account_resource_storage_item`으로 올린다
(2단계 presigned 방식). 올린 뒤 `asset_update_resource_storage_info`로
`filter_mode=Point` / `wrap_mode=Clamp` / `pivot 0.5,0.5`를 건다.

> ⚠ **`asset_update_resource_storage_info`는 생략한 필드를 지운다.**
> `properties`만 넘겼더니 name·description·subcategory가 전부 빈 문자열이 됐다.
> 고칠 때는 **네 개를 항상 같이** 넘길 것.

## 올라간 RUID

| 스킬 | 파일 | RUID |
|---|---|---|
| 몸통 박치기 | `skill-snail-tackle.svg` | `518cc119c1c04b8797090175d9f015f2` |
| 푸른 껍질 | `skill-blueshell-guard.svg` | `73c1bdafcb7e42bc8db0041883226449` |
| 포자 살포 | `skill-spore-spray.svg` | `6923ce8064e4445d8e63176645943fb1` |
| 뿔 들이받기 | `skill-horn-gore.svg` | `0928f98bbd114efc935696c1200c9d39` |
| 바위 던지기 | `skill-rock-throw.svg` | `cba9471e009f46ee9c786f31d29c3848` |

**그림을 고치면 새로 올려 RUID를 바꾸고 `SkillTable.csv`의 `icon_ruid`도 같이 고칠 것.**
기존 RUID의 그림만 바꾸려면 `asset_update_resource_storage_data`를 쓴다.
