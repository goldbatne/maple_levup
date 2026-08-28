# 몬스터 스킬 아이콘 원본 (T20-6 · T32-2 · T37-2)

몬스터 스킬 **17종**의 아이콘을 **직접 그렸다.** 여기 있는 것이 그 원본이다 —
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
  그래서 `SkillTable.icon_ratio`는 17종 전부 `1.00`이다.
- **판(plate)은 17장이 완전히 같다.** `draw-icons.cjs`의 `PLATE` 한 곳에서 찍는다.
  원작 스킬 아이콘과 같은 틀이라 스킬 창에서 "재료"가 아니라 "스킬"로 읽힌다.
- **각 스킬은 색이 겹치지 않는다.** 헤네시스 5종이 청록 / 파랑 / 주황+초록 / 베이지+노랑 /
  회색을 쓰므로, 페리온 7종은 호박+은 / 보라 / 적갈 / 철청+금 / 아이보리+자주 / 주황빨강 /
  황토+노랑으로, 엘리니아 5종은 연두 / 밤색+나이테 / 밝은 청록 / 분홍 / 검정+진홍으로
  갈랐다. 격자에서 이름을 안 읽어도 구분된다.
- ⚠⚠ **그려 놓고 반드시 눈으로 볼 것. 두 번 다 여기서 걸렸다.**
  T32-2에서 7종 중 **4종**, T37-2에서 5종 중 **4종**이 안 읽혔다.
  틀린 것이 "덜 예쁘다"가 아니라 **다른 물건으로 보인다**는 것이 문제다:
  | | 그리려던 것 | 실제로 보인 것 |
  |---|---|---|
  | T32-2 | 어둠의 뿌리 | 보라 성문 |
  | | 뼈 무덤 | 탁자 다리 |
  | | 대지 가르기 | 모자 |
  | | 저돌 맹진 | 갈색 덩어리 |
  | T37-2 | 단단한 밑동 | **솥** (두 번) |
  | | 물방울 터뜨리기 | **보석** |
  | | 어둠의 손아귀 | **벌레 → 촛불 케이크 → 빨간 보석 박은 덩어리** (세 번) |
  기존 것과 **나란히 놓은 대조 시트를 4배**로 뽑아 보고 다시 그린다.
  세부를 볼 때는 **8배**로 한 번 더 본다.
- ⚠ **28칸에서 손·그루터기 같은 것은 실루엣으로만 읽힌다.** 굵기·마디·기운을
  더할수록 덩어리가 된다. 손아귀는 손가락을 **셋으로 줄이고 손목을 화면 밖으로
  빼서야** 손이 됐고(손목이 없으면 몸통이 되어 거미로 읽힌다), 그루터기는
  **비스듬한 각도를 버리고 단면을 정면으로** 놓아야 나무가 됐다
  (어두운 몸통 + 밝은 윗면 타원 + 아래 뿌리 = 어떻게 그려도 솥이다).
- ⚠ **동심원을 그릴 때 폭만 깎으면 안쪽이 네모가 된다.** 가로세로를 같은 비율로
  줄여야 한다 (`STUMP`의 `disc(k)` 참조 — 처음에 반지름을 정수로 빼다가
  가운데 고리가 막대가 됐다).
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

### 페리온 7종 (T32-2)

| 스킬 | 파일 | RUID |
|---|---|---|
| 도끼 휘두르기 | `skill-axe-swing.svg` | `b03001aaa4cf4dfe82d34a48c58cb342` |
| 어둠의 뿌리 | `skill-dark-root.svg` | `0fbbe12552664c5f87944ff56a630178` |
| 저돌 맹진 | `skill-boar-charge.svg` | `b656b6744e204375a345782b5119aea2` |
| 강철 가죽 | `skill-iron-hide.svg` | `da712fe9654b4ea2940cee669043bceb` |
| 뼈 무덤 | `skill-bone-grave.svg` | `637abac61bd14f788b157d6aaf1fa08f` |
| 화염 돌풍 | `skill-fire-burst.svg` | `f960bb921fb44bea91c95ea6b95f1d85` |
| 대지 가르기 | `skill-earth-rend.svg` | `383249b0f9254764aa758b1bcc9bfee9` |

### 엘리니아 5종 (T37-2)

| 스킬 | 파일 | RUID |
|---|---|---|
| 끈적한 몸통 | `skill-slime-body.svg` | `72d1dd0939714240bddc0b6865eb93ce` |
| 단단한 밑동 | `skill-stump-bark.svg` | `8061aa7a332b4e7ba783b3cd582ebb4b` |
| 물방울 터뜨리기 | `skill-bubble-burst.svg` | `572a7a12dcb449bcb0582fc2ccf5be07` |
| 요정의 인분 | `skill-fairy-dust.svg` | `5f5ebe88b8f2426195c793b3440012e4` |
| 어둠의 손아귀 | `skill-dark-grip.svg` | `c07ed26000af460a8438a3486e16f3ec` |

**그림을 고치면 새로 올려 RUID를 바꾸고 `SkillTable.csv`의 `icon_ruid`도 같이 고칠 것.**
기존 RUID의 그림만 바꾸려면 `asset_update_resource_storage_data`를 쓴다.
