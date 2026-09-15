# AREA 00 VALIDATION REPORT

기계 검사는 최종 개별 PNG를 대상으로 수행했습니다. 안전영역은 각 프레임의 non-zero alpha bounding box가 canvas의 가로/세로 85% 이하인지 검사했습니다.

## 001 달팽이 / 이슬 미끄럼길

- Expected frames: 8 / Actual: 8
- VFX canvas: 384×384 RGBA
- ICON: 256×256 RGBA
- Common VFX transform: `{'source_union': (0, 0, 418, 418), 'scale': 0.7257416267942584, 'offset': (40, 40)}`
- Result: **PASS**

| Frame | Mode | Size | Alpha | Partial alpha | bbox ratio W/H | 85% safe | SHA256 |
|---|---|---|---|---|---|---|---|
| F00 | RGBA | 384×384 | 0–255 | Y | 0.789/0.753 | PASS | `5c688913af6b8da5…` |
| F01 | RGBA | 384×384 | 0–255 | Y | 0.789/0.701 | PASS | `8d2b6cf39cb4ddc2…` |
| F02 | RGBA | 384×384 | 0–255 | Y | 0.763/0.747 | PASS | `d6f029bb4b11b2a2…` |
| F03 | RGBA | 384×384 | 0–255 | Y | 0.789/0.789 | PASS | `e19018ad1c1f0023…` |
| F04 | RGBA | 384×384 | 0–255 | Y | 0.786/0.781 | PASS | `2e5a59b39ebee891…` |
| F05 | RGBA | 384×384 | 0–255 | Y | 0.755/0.779 | PASS | `dfeaf85e57f4b653…` |
| F06 | RGBA | 384×384 | 0–255 | Y | 0.789/0.786 | PASS | `583e882ff1eb90dc…` |
| F07 | RGBA | 384×384 | 0–255 | Y | 0.789/0.776 | PASS | `061184c16c288eb9…` |

- ICON validation: **PASS**
- Alpha edge composite: `monsters/001_m_snail_달팽이/PREVIEW/alpha_edge_check.png` (white / middle gray / black)

## 002 파란 달팽이 / 푸른 껍질

- Expected frames: 8 / Actual: 8
- VFX canvas: 256×256 RGBA
- ICON: 256×256 RGBA
- Common VFX transform: `{'source_union': (0, 0, 418, 418), 'scale': 0.4838277511961723, 'offset': (27, 27)}`
- Result: **PASS**

| Frame | Mode | Size | Alpha | Partial alpha | bbox ratio W/H | 85% safe | SHA256 |
|---|---|---|---|---|---|---|---|
| F00 | RGBA | 256×256 | 0–255 | Y | 0.723/0.570 | PASS | `aaa38cb2a132dfa9…` |
| F01 | RGBA | 256×256 | 0–253 | Y | 0.789/0.758 | PASS | `300332c6a1a23768…` |
| F02 | RGBA | 256×256 | 0–253 | Y | 0.762/0.754 | PASS | `9e9228b737057e1c…` |
| F03 | RGBA | 256×256 | 0–255 | Y | 0.789/0.789 | PASS | `ce44cc343e60cc7f…` |
| F04 | RGBA | 256×256 | 0–254 | Y | 0.789/0.773 | PASS | `a0c2a27687ad2db1…` |
| F05 | RGBA | 256×256 | 0–253 | Y | 0.762/0.789 | PASS | `9285504ded7a7b49…` |
| F06 | RGBA | 256×256 | 0–255 | Y | 0.789/0.762 | PASS | `b076875693be41a4…` |
| F07 | RGBA | 256×256 | 0–253 | Y | 0.785/0.719 | PASS | `4e2aa7a27064bf08…` |

- ICON validation: **PASS**
- Alpha edge composite: `monsters/002_m_blue_snail_파란 달팽이/PREVIEW/alpha_edge_check.png` (white / middle gray / black)

## 003 빨간 달팽이 / 붉은 껍질 돌진

- Expected frames: 8 / Actual: 8
- VFX canvas: 256×256 RGBA
- ICON: 256×256 RGBA
- Common VFX transform: `{'source_union': (0, 0, 418, 418), 'scale': 0.4838277511961723, 'offset': (27, 27)}`
- Result: **PASS**

| Frame | Mode | Size | Alpha | Partial alpha | bbox ratio W/H | 85% safe | SHA256 |
|---|---|---|---|---|---|---|---|
| F00 | RGBA | 256×256 | 0–255 | Y | 0.730/0.754 | PASS | `dd971349d23fa14e…` |
| F01 | RGBA | 256×256 | 0–255 | Y | 0.789/0.688 | PASS | `82ffa9d5f8edf879…` |
| F02 | RGBA | 256×256 | 0–255 | Y | 0.750/0.730 | PASS | `ae57ecf0bc64a924…` |
| F03 | RGBA | 256×256 | 0–255 | Y | 0.770/0.789 | PASS | `0288d32484f4a447…` |
| F04 | RGBA | 256×256 | 0–254 | Y | 0.777/0.746 | PASS | `ae5948c6e2d46e12…` |
| F05 | RGBA | 256×256 | 0–255 | Y | 0.766/0.715 | PASS | `45a51e41e23bd8c3…` |
| F06 | RGBA | 256×256 | 0–255 | Y | 0.723/0.746 | PASS | `a30b224c35f9c291…` |
| F07 | RGBA | 256×256 | 0–253 | Y | 0.789/0.699 | PASS | `65ad00e4ab6adecb…` |

- ICON validation: **PASS**
- Alpha edge composite: `monsters/003_m_red_snail_빨간 달팽이/PREVIEW/alpha_edge_check.png` (white / middle gray / black)

## 004 마노 / 마노의 무지개 파동

- Expected frames: 12 / Actual: 12
- VFX canvas: 512×512 RGBA
- ICON: 256×256 RGBA
- Common VFX transform: `{'source_union': (0, 0, 314, 314), 'scale': 1.2881528662420383, 'offset': (54, 54)}`
- Result: **PASS**

| Frame | Mode | Size | Alpha | Partial alpha | bbox ratio W/H | 85% safe | SHA256 |
|---|---|---|---|---|---|---|---|
| F00 | RGBA | 512×512 | 0–252 | Y | 0.789/0.748 | PASS | `4ad17b253e32be56…` |
| F01 | RGBA | 512×512 | 0–252 | Y | 0.787/0.768 | PASS | `4540fc95cb489a9e…` |
| F02 | RGBA | 512×512 | 0–255 | Y | 0.770/0.746 | PASS | `698042c3788f6eeb…` |
| F03 | RGBA | 512×512 | 0–254 | Y | 0.734/0.746 | PASS | `0e28d7c498ebf89f…` |
| F04 | RGBA | 512×512 | 0–253 | Y | 0.789/0.758 | PASS | `0f2461ab22319a7b…` |
| F05 | RGBA | 512×512 | 0–253 | Y | 0.787/0.787 | PASS | `1be3de6601b33bd9…` |
| F06 | RGBA | 512×512 | 0–253 | Y | 0.787/0.787 | PASS | `b1e0c6d4c195a1d7…` |
| F07 | RGBA | 512×512 | 0–255 | Y | 0.789/0.787 | PASS | `d94b107a105780ca…` |
| F08 | RGBA | 512×512 | 0–253 | Y | 0.789/0.787 | PASS | `06531de52a3ffeb0…` |
| F09 | RGBA | 512×512 | 0–253 | Y | 0.787/0.787 | PASS | `9d5576ae87c57c8c…` |
| F10 | RGBA | 512×512 | 0–253 | Y | 0.787/0.787 | PASS | `11647b5f0680b377…` |
| F11 | RGBA | 512×512 | 0–253 | Y | 0.754/0.787 | PASS | `35089115f2369684…` |

- ICON validation: **PASS**
- Alpha edge composite: `monsters/004_m_mano_마노/PREVIEW/alpha_edge_check.png` (white / middle gray / black)

## 005 슬라임 / 끈적한 몸통

- Expected frames: 8 / Actual: 8
- VFX canvas: 256×256 RGBA
- ICON: 256×256 RGBA
- Common VFX transform: `{'source_union': (0, 0, 418, 418), 'scale': 0.4838277511961723, 'offset': (27, 27)}`
- Result: **PASS**

| Frame | Mode | Size | Alpha | Partial alpha | bbox ratio W/H | 85% safe | SHA256 |
|---|---|---|---|---|---|---|---|
| F00 | RGBA | 256×256 | 0–255 | Y | 0.789/0.543 | PASS | `d1d7d5865fb9d05c…` |
| F01 | RGBA | 256×256 | 0–255 | Y | 0.789/0.715 | PASS | `5b2581ef8dcbb266…` |
| F02 | RGBA | 256×256 | 0–255 | Y | 0.734/0.691 | PASS | `d8af609ae4de75ec…` |
| F03 | RGBA | 256×256 | 0–255 | Y | 0.758/0.641 | PASS | `ebe6ed00b1eb4949…` |
| F04 | RGBA | 256×256 | 0–255 | Y | 0.789/0.746 | PASS | `a06cd52466d44d04…` |
| F05 | RGBA | 256×256 | 0–255 | Y | 0.707/0.703 | PASS | `02cf0c6434c6bce1…` |
| F06 | RGBA | 256×256 | 0–255 | Y | 0.746/0.672 | PASS | `a4a147dc9162a3b8…` |
| F07 | RGBA | 256×256 | 0–255 | Y | 0.789/0.723 | PASS | `412234d87d29cbf8…` |

- ICON validation: **PASS**
- Alpha edge composite: `monsters/005_m_slime_슬라임/PREVIEW/alpha_edge_check.png` (white / middle gray / black)

# Overall: **PASS**
