"""지역 전용 RectTile 타일셋 이미지를 찍어낸다.

대표 지시(2026-08-29): "타일 있잖아 이거 답답하네 그냥 색 타일 새로 그거에 맞게
만들어서 해주면 안되려나?"

기존 `RectTileData_Henesys` 하나로 모든 지역을 칠하다 보니 어느 지역이든
헤네시스의 밝은 잔디였다. 여기서 **지역 색으로 룰타일 16종을 생성**한다.

## 룰타일 16종은 코너 넷의 조합이다
타일 하나의 네 모서리(NW/NE/SW/SE)가 각각 바닥(A)인지 길(B)인지로 16가지다.
픽셀마다 **네 코너 값을 이중선형 보간**해 0.5를 넘으면 B로 칠하면
경계가 저절로 둥글게 이어진다 — 원작 헤네시스 타일셋과 같은 구조다
(그 61종의 모서리 잔디 비율을 재서 알아냈다, T43-2).

## 쓰는 법
    python gen_tileset.py <출력폴더> <프리셋이름>
프리셋을 더하면 지역이 하나 늘어난다 — **색만 바꾸면 된다.**
"""
import sys, os, math, random

from PIL import Image

SIZE = 64          # 시험에서 64x64가 정상으로 들어갔다 (1 world unit에 맞춰 늘어난다)

# 지역 프리셋: (바닥색, 길색, 바닥 얼룩색들, 길 얼룩색들, 경계 테두리색)
PRESETS = {
    # 엘리니아 = 정글. 어두운 이끼 바닥 + 축축한 진흙길.
    "jungle": dict(
        a=(58, 102, 44), b=(92, 72, 48),
        a_spots=[(46, 86, 36), (70, 118, 52), (40, 78, 34), (64, 110, 60)],
        b_spots=[(80, 62, 40), (104, 84, 56), (74, 58, 38)],
        edge=(34, 60, 28),
    ),
}


def bilinear(nw, ne, sw, se, u, v):
    """v: 아래 0 → 위 1. 네 코너를 이중선형 보간한다."""
    return (nw * (1 - u) * v + ne * u * v
            + sw * (1 - u) * (1 - v) + se * u * (1 - v))


def make_tile(bits, cfg, seed):
    """bits: NW=8 NE=4 SW=2 SE=1 (켜져 있으면 길 B)."""
    rnd = random.Random(seed)
    nw = 1.0 if bits & 8 else 0.0
    ne = 1.0 if bits & 4 else 0.0
    sw = 1.0 if bits & 2 else 0.0
    se = 1.0 if bits & 1 else 0.0

    img = Image.new("RGBA", (SIZE, SIZE))
    px = img.load()
    # 경계를 딱딱하지 않게 흔드는 저주파 잡음
    ph1, ph2 = rnd.random() * 6.28, rnd.random() * 6.28

    for y in range(SIZE):
        for x in range(SIZE):
            u = x / (SIZE - 1)
            v = 1 - y / (SIZE - 1)
            w = bilinear(nw, ne, sw, se, u, v)
            # 경계 흔들기 (전부 A거나 전부 B면 흔들 필요가 없다)
            if 0 < bits < 15:
                w += 0.055 * math.sin(u * 9.0 + ph1) + 0.045 * math.sin(v * 11.0 + ph2)
            is_b = w > 0.5
            base = cfg["b"] if is_b else cfg["a"]
            px[x, y] = base + (255,)

    # 경계선 — 원작 타일처럼 A/B가 만나는 자리에 어두운 실선을 한 겹 긋는다
    if 0 < bits < 15:
        edge = cfg["edge"] + (255,)
        for y in range(SIZE):
            for x in range(SIZE):
                if px[x, y][:3] != cfg["b"]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < SIZE and 0 <= ny < SIZE and px[nx, ny][:3] == cfg["a"]:
                        px[x, y] = edge
                        break

    # 얼룩 — 단색이면 평평해 보인다
    for _ in range(SIZE * SIZE // 6):
        x, y = rnd.randrange(SIZE), rnd.randrange(SIZE)
        cur = px[x, y][:3]
        if cur == cfg["a"]:
            px[x, y] = rnd.choice(cfg["a_spots"]) + (255,)
        elif cur == cfg["b"]:
            px[x, y] = rnd.choice(cfg["b_spots"]) + (255,)
    return img


# 인덱스 순서 = .tileset의 datas[] 순서 = .map의 tileIndex
# ⚠ 이 순서를 바꾸면 이미 칠한 맵의 tileIndex가 전부 어긋난다 (tile.md 경고).
# 바닥은 가장 많이 깔리므로 **변주 셋**을 둔다 — 한 종만 쓰면 같은 얼룩이 반복돼
# 격자 무늬처럼 보인다 (이어 붙여 보고 알았다).
ORDER = [
    (0,  "floor_1", 0), (0, "floor_2", 7), (0, "floor_3", 21),
    (15, "path", 0),
    (1,  "se", 0), (2, "sw", 0), (4, "ne", 0), (8, "nw", 0),
    (3,  "s_half", 0), (12, "n_half", 0), (5, "e_half", 0), (10, "w_half", 0),
    (7,  "nw_a", 0), (11, "ne_a", 0), (13, "sw_a", 0), (14, "se_a", 0),
    (9,  "diag_nwse", 0), (6, "diag_nesw", 0),
]


def main():
    out = sys.argv[1]
    name = sys.argv[2]
    cfg = PRESETS[name]
    os.makedirs(out, exist_ok=True)
    for i, (bits, label, salt) in enumerate(ORDER):
        img = make_tile(bits, cfg, seed=1000 + bits + salt * 137)
        f = os.path.join(out, "%02d_%s.png" % (i, label))
        img.save(f)
        print("%2d %-10s bits=%2d  %s  %d bytes" % (i, label, bits, f, os.path.getsize(f)))


if __name__ == "__main__":
    main()
