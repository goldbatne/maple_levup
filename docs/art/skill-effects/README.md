# 몬스터 스킬 시전 이펙트 원본 (T21-1)

몬스터 스킬 4종의 **시전 이펙트**를 직접 그렸다. 아이콘(`../skill-icons/`)과
같은 방식이고, 다른 점은 **월드에 뜨는 그림**이라는 것뿐이다.

## 왜 한 장짜리 그림인가

`asset_create_account_resource_storage_item`이 받는 category가
**sprite / audioclip / avataritem뿐이라 animationclip은 올릴 길이 없다.**
그래서 `_EffectService:PlayEffectAttached`(클립 재생)를 못 쓴다.

대신 **한 장을 띄워 놓고 `Combat/SkillCastEffect.mlua`가 움직인다** —
커지고, 옅어지고, 돌고, 흐른다. 여러 장을 올려 프레임을 갈아끼우는 길도 있지만
(SpriteRUID 교체는 T11-1에서 쓴 방법) 4종 × 5장 = 20장을 올려야 하고 그림마다
프레임 수를 따로 관리해야 한다. 한 장 + 움직임이 싸고, 고칠 때도 한 장만 다시 올린다.

## 스타일 (`SkillTable.effect_style`)

| style | 스킬 | 움직임 |
|---|---|---|
| `burst` | 몸통 박치기 | 확 커지며 조금 돈다 |
| `ring` | 푸른 껍질 | 천천히 커진다 (안 돈다 — 돌면 고리가 어지럽다) |
| `cloud` | 포자 살포 | 부풀며 위로 떠오른다 |
| `pierce` | 뿔 들이받기 | 앞으로 나가며 길어진다 |

`effect_style`이 **비어 있으면** `effect_ruid`는 원작 애니메이션 클립이고
`_EffectService`가 그대로 재생한다(히어로 5종). 채워져 있으면 우리 스프라이트다.
⚠ **칸을 나눈 이유**: 한 칸에 섞으면 런타임에 클립인지 그림인지 알 방법이 없고,
클립 자리에 그림을 넣으면 **에러 없이 안 뜬다.**

## ⚠ 실측으로 배운 것 셋

1. **그리기 순서.** `OrderInLayer` 6으로는 **캐릭터 뒤에 깔린다.** 500으로 올렸다.
2. **크기.** 96px = 1 월드 유닛이라 배율 1.0이면 사람만 하다. 캐릭터(약 1.4 유닛)보다
   커야 연출로 읽힌다 — 지금은 최대 2.7까지 커진다.
3. **투명도는 끝에서만 뺀다.** 처음부터 `1 - t`로 옅어지게 했더니 0.4초짜리 연출이
   뜨자마자 배경에 묻혀 "번쩍했나?" 수준이 됐다. 지금은 t가 0.5~0.65를 넘어서야 빠진다.

그리고 **이펙트는 아이콘과 색을 똑같이 두면 안 될 때가 있다.** 포자 구름을 아이콘과
같은 초록으로 뒀더니 **잔디 위에서 묻혔다.** 이펙트는 아무 배경 위에나 뜨므로
색조가 아니라 **명도 대비**로 버텨야 한다 — 테두리를 거의 검게, 속을 거의 흰 노랑으로 벌렸다.

## 고치는 방법

```bash
node docs/art/skill-effects/draw-effects.cjs
python docs/art/skill-effects/rasterize.py docs/art/skill-effects/fx-spore-cloud.svg out.png 2
```

48×48 격자를 2배로 뽑아 96×96이 된다. 아이콘과 달리 화면에서 확대·축소되므로
격자가 정확히 맞아떨어질 필요는 없다.

**이미 올린 그림만 갈고 싶으면** `asset_update_resource_storage_data`를 쓴다 —
RUID가 유지되므로 `SkillTable`을 안 고쳐도 된다.

> ⚠ `asset_update_resource_storage_info`(메타데이터)는 **생략한 필드를 지운다.**
> name·description·subcategory·properties를 항상 같이 넘길 것.

## 올라간 RUID

| 스킬 | 파일 | RUID |
|---|---|---|
| 몸통 박치기 | `fx-snail-impact.svg` | `66dcf54b85cc464281802bda30682582` |
| 푸른 껍질 | `fx-blueshell-guard.svg` | `bb1f9e3df5a443caa1294d9fd99113cc` |
| 포자 살포 | `fx-spore-cloud.svg` | `7985d900fb03443899423346524299a7` |
| 뿔 들이받기 | `fx-horn-pierce.svg` | `2afb9097de824da797992930d21e2d70` |

**바위 던지기는 시전 이펙트가 없다** — 날아가는 바위가 곧 연출이다 (T19-4).
