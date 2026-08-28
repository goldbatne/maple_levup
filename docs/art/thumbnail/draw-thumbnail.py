# "메이플 레벨업" 대표 이미지 — 처음부터 직접 그린다.
#
# 대표 지시: "아무것도 없이 ... 제작한다고 생각해서", "토벤머리가 다양한 스킬들을
# 써서 몬스터와 전투하는 구도".
#
# 방침: 오려 붙이지 않고 도형으로 그린다. 2배로 그린 뒤 줄여서(supersampling)
#       곡선 가장자리를 매끄럽게 만든다 — 픽셀로 찍으면 계단이 보인다.
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SS = 2                      # 확대 배율 (그릴 때만)
W, H = 1280 * SS, 720 * SS
CX, CY = int(W * 0.33), int(H * 0.50)     # 주인공 자리

base = Image.new("RGB", (W, H), (14, 16, 30))
d = ImageDraw.Draw(base)

def px(v): return int(v * SS)

# ── 배경: 가운데가 밝은 방사형 ─────────────────────────────────
# 그라데이션 API를 안 쓰고 동심원을 겹쳐 만든다. 단수를 촘촘히 두면 티가 안 난다.
STEPS = 120
R_MAX = int(math.hypot(W, H))
for i in range(STEPS, 0, -1):
    t = i / STEPS
    r = int(R_MAX * t)
    c = (int(14 + 44 * (1 - t) ** 1.6),
         int(16 + 30 * (1 - t) ** 1.6),
         int(30 + 78 * (1 - t) ** 1.6))
    d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=c)

# ── 배경: 뻗어 나가는 속도선 ───────────────────────────────────
rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rays)
for i in range(28):
    a = math.radians(i * (360 / 28) + 7)
    w0 = px(2 + (i % 3) * 5)
    x1, y1 = CX + R_MAX * math.cos(a), CY + R_MAX * math.sin(a)
    rd.line([CX, CY, x1, y1], fill=(120, 150, 220, 26), width=w0)
base = Image.alpha_composite(base.convert("RGBA"), rays)
d = ImageDraw.Draw(base)

def glow(img, cx, cy, r, color, steps=26, power=1.9):
    """부드러운 빛무리. 동심원의 투명도를 점점 낮춘다."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(lay)
    for i in range(steps, 0, -1):
        t = i / steps
        rr = int(r * t)
        a = int(color[3] * (1 - t) ** power)
        g.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(color[0], color[1], color[2], a))
    return Image.alpha_composite(img, lay)

def star(g, cx, cy, r_out, r_in, n, color, rot=0):
    pts = []
    for i in range(n * 2):
        rr = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    g.polygon(pts, fill=color)

def crescent(img, cx, cy, r_out, r_in, a0, a1, color):
    """휘두른 자국. 바깥 부채꼴에서 안쪽을 파낸다."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(lay)
    g.pieslice([cx - r_out, cy - r_out, cx + r_out, cy + r_out], a0, a1, fill=color)
    g.pieslice([cx - r_in, cy - r_in, cx + r_in, cy + r_in], a0 - 4, a1 + 4, fill=(0, 0, 0, 0))
    return Image.alpha_composite(img, lay)

# ── 몬스터: 오른쪽에서 몰려온다 ────────────────────────────────
def snail(g, x, y, s, shell=(34, 150, 132), shell2=(18, 96, 86)):
    body = (238, 226, 200)
    g.ellipse([x - 34*s, y - 12*s, x + 30*s, y + 16*s], fill=body,
              outline=(30, 30, 40), width=px(3))
    g.ellipse([x - 12*s, y - 34*s, x + 34*s, y + 12*s], fill=shell,
              outline=(30, 30, 40), width=px(3))
    g.arc([x - 2*s, y - 24*s, x + 24*s, y + 2*s], 0, 360, fill=shell2, width=px(5))
    g.arc([x + 4*s, y - 18*s, x + 18*s, y - 4*s], 0, 360, fill=shell2, width=px(4))
    for dx in (-26, -18):
        g.line([x + dx*s, y - 10*s, x + (dx - 4)*s, y - 26*s], fill=(30, 30, 40), width=px(3))
        g.ellipse([x + (dx-7)*s, y - 30*s, x + (dx-1)*s, y - 24*s], fill=(30, 30, 40))
    g.ellipse([x - 24*s, y - 6*s, x - 18*s, y + 0*s], fill=(30, 30, 40))

def mushroom(g, x, y, s, cap=(240, 130, 40), cap2=(255, 196, 60)):
    body = (244, 236, 214)
    g.ellipse([x - 22*s, y - 8*s, x + 22*s, y + 26*s], fill=body,
              outline=(30, 30, 40), width=px(3))
    g.pieslice([x - 34*s, y - 34*s, x + 34*s, y + 18*s], 180, 360, fill=cap,
               outline=(30, 30, 40), width=px(3))
    for ox, oy, rr in ((-18, -16, 6), (2, -22, 8), (20, -14, 5)):
        g.ellipse([x + (ox-rr)*s, y + (oy-rr)*s, x + (ox+rr)*s, y + (oy+rr)*s], fill=cap2)
    g.ellipse([x - 10*s, y + 4*s, x - 5*s, y + 10*s], fill=(30, 30, 40))
    g.ellipse([x + 5*s, y + 4*s, x + 10*s, y + 10*s], fill=(30, 30, 40))

def golem(g, x, y, s, rock=(150, 146, 138), rock2=(104, 100, 94)):
    def blk(cx, cy, w, h, c):
        g.rounded_rectangle([x + (cx-w)*s, y + (cy-h)*s, x + (cx+w)*s, y + (cy+h)*s],
                            radius=px(6), fill=c, outline=(30, 30, 40), width=px(3))
    # ⚠ 팔을 ±34에 뒀더니 몸통(폭 30)과 **떨어져** 블록이 흩어져 보였다.
    #   어깨가 몸통에 물리도록 ±30으로 당긴다.
    blk(-14, 40, 11, 12, rock2); blk(14, 40, 11, 12, rock2)     # 다리
    blk(-30, 2, 11, 20, rock2); blk(30, 2, 11, 20, rock2)       # 팔
    blk(0, 6, 30, 26, rock)                                     # 몸통
    blk(0, -26, 21, 16, rock)                                   # 머리
    for ex in (-11, 3):
        g.ellipse([x + ex*s, y - 32*s, x + (ex+8)*s, y - 24*s], fill=(255, 210, 70))
    g.line([x - 16*s, y + 14*s, x + 16*s, y + 14*s], fill=rock2, width=px(4))

# ── 주인공(토벤머리) ───────────────────────────────────────────
def hero(g, x, y, s):
    """오른쪽을 향해 검을 내지른 치비.

    ⚠ 처음엔 부위를 각자 좌표로 찍었더니 **팔다리가 몸에서 떨어졌다.**
      그래서 어깨·골반 같은 이음매를 먼저 정하고 거기서 뻗어 나가게 고쳤다.
    """
    HAIR, HAIR2 = (28, 26, 36), (66, 62, 84)
    SKIN, LINE = (247, 216, 184), (24, 24, 32)
    SHIRT, SHIRT2 = (200, 226, 246), (146, 182, 216)
    PANT, PANT2 = (40, 66, 152), (26, 44, 108)
    BOOT = (48, 72, 112)
    BLADE, BLADE2, HILT = (232, 240, 250), (166, 182, 204), (198, 208, 122)
    LW = max(px(3), int(s * 0.55))

    def P(a, b): return (x + a * s, y + b * s)
    SHO_F, SHO_B, HIP = (14, 2), (-14, 2), (0, 26)

    # 뒤쪽 팔 · 다리 (몸통보다 먼저 = 뒤에 깔린다)
    g.line([P(*SHO_B), P(-34, 20)], fill=SKIN, width=int(9 * s))
    g.ellipse([*P(-40, 14), *P(-26, 28)], fill=SKIN, outline=LINE, width=LW)
    g.line([P(-6, 24), P(-20, 50)], fill=PANT2, width=int(12 * s))
    g.ellipse([*P(-30, 44), *P(-12, 58)], fill=BOOT, outline=LINE, width=LW)

    # 몸통
    g.polygon([P(-19, -2), P(19, -2), P(15, 30), P(-15, 30)],
              fill=SHIRT, outline=LINE, width=LW)
    g.polygon([P(3, -2), P(19, -2), P(15, 30), P(2, 30)], fill=SHIRT2)

    # 앞쪽 다리
    g.line([P(6, 24), P(16, 50)], fill=PANT, width=int(13 * s))
    g.ellipse([*P(8, 46), *P(28, 60)], fill=BOOT, outline=LINE, width=LW)

    # 앞으로 뻗은 팔 + 검
    g.line([P(*SHO_F), P(48, 12)], fill=SKIN, width=int(11 * s))
    g.line([P(*SHO_F), P(48, 12)], fill=LINE, width=LW)
    g.line([P(*SHO_F), P(48, 12)], fill=SKIN, width=int(11 * s) - LW * 2)
    g.ellipse([*P(42, 5), *P(58, 21)], fill=SKIN, outline=LINE, width=LW)
    g.polygon([P(52, 2), P(60, 2), P(60, 24), P(52, 24)], fill=HILT, outline=LINE, width=LW)
    g.polygon([P(60, 6), P(112, -2), P(126, 10), P(112, 22), P(60, 20)],
              fill=BLADE, outline=LINE, width=LW)
    g.polygon([P(62, 14), P(110, 12), P(120, 11), P(110, 19), P(62, 19)], fill=BLADE2)

    # 머리
    g.ellipse([*P(-27, -60), *P(23, -8)], fill=SKIN, outline=LINE, width=LW)
    g.chord([*P(-29, -64), *P(25, -8)], 178, 362, fill=HAIR)
    g.polygon([P(-29, -34), P(-24, -54), P(-8, -62), P(10, -58), P(23, -44),
               P(20, -30), P(10, -46), P(-6, -42), P(-18, -30)], fill=HAIR)
    g.ellipse([*P(-11, -80), *P(9, -60)], fill=HAIR)               # 상투
    g.line([P(-2, -54), P(8, -46)], fill=HAIR2, width=int(1.6 * s))
    # 눈
    for ex in (-13, 6):
        g.ellipse([*P(ex, -36), *P(ex + 9, -24)], fill=(30, 30, 38))
        g.ellipse([*P(ex + 2, -34), *P(ex + 5, -31)], fill=(255, 255, 255))

# ── 그리기 ─────────────────────────────────────────────────────
img = base

# ⚠ 처음엔 인물 s=1.9로 그렸더니 **화면에서 60픽셀짜리 점**이 됐다.
#   hero()의 좌표가 ±60 단위라 s가 곧 "단위당 픽셀"이다 —
#   최종 400px로 보이려면 (2배로 그리니까) s ≈ 7이 필요하다.

# 몬스터 — 오른쪽에서 몰려온다
g = ImageDraw.Draw(img)
golem(g, px(1015), px(300), 4.4)
mushroom(g, px(900), px(495), 3.4)
snail(g, px(770), px(140), 3.6)
snail(g, px(1200), px(470), 2.6)

# 스킬 1 — 크게 휘두른 자국 (인물 → 몬스터로 이어진다)
img = crescent(img, CX + px(70), CY - px(30), px(430), px(330), -74, 40, (255, 246, 210, 225))
img = crescent(img, CX + px(70), CY - px(30), px(400), px(356), -66, 32, (255, 206, 64, 255))

# 스킬 2 — 포자 구름
for ox, oy, rr in ((1120, 130, 84), (1210, 90, 62), (1180, 210, 58)):
    img = glow(img, px(ox), px(oy), px(rr) * 2, (150, 220, 70, 150))
g = ImageDraw.Draw(img)
for ox, oy, rr in ((1120, 130, 66), (1210, 90, 48), (1180, 210, 44)):
    g.ellipse([px(ox - rr), px(oy - rr), px(ox + rr), px(oy + rr)], fill=(168, 216, 78))
for ox, oy, rr in ((1102, 116, 26), (1202, 78, 18)):
    g.ellipse([px(ox - rr), px(oy - rr), px(ox + rr), px(oy + rr)], fill=(226, 250, 160))

# 스킬 3 — 방어막 고리 (인물을 감싼다)
lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
lg = ImageDraw.Draw(lay)
for rr, a in ((252, 200), (236, 110), (270, 70)):
    lg.ellipse([CX - px(rr), CY - px(rr) * 0.80, CX + px(rr), CY + px(rr) * 0.80],
               outline=(120, 190, 255, a), width=px(8))
img = Image.alpha_composite(img, lay)

# 스킬 4 — 날아가는 바위
g = ImageDraw.Draw(img)
for ox, oy, rr in ((150, 250, 34), (250, 190, 22), (95, 330, 15)):
    g.ellipse([px(ox - rr), px(oy - rr), px(ox + rr), px(oy + rr)],
              fill=(148, 144, 138), outline=(30, 30, 40), width=px(4))

# 주인공
g = ImageDraw.Draw(img)
hero(g, CX, CY - px(20), 5.4)

# 스킬 5 — 부딪히는 충격 (몬스터 쪽)
for ox, oy, rr in ((950, 300, 120), (760, 560, 88), (1240, 580, 66)):
    img = glow(img, px(ox), px(oy), px(rr) * 2, (255, 216, 90, 190))
g = ImageDraw.Draw(img)
for ox, oy, rr, rot in ((950, 300, 96, 8), (760, 560, 70, 24), (1240, 580, 52, 0)):
    star(g, px(ox), px(oy), px(rr), px(rr) * 0.40, 8, (255, 232, 140), rot)
    star(g, px(ox), px(oy), px(rr) * 0.62, px(rr) * 0.24, 8, (255, 255, 255), rot)

# 반짝이는 알갱이
import random
random.seed(7)
for _ in range(70):
    x = random.randint(0, W); y = random.randint(0, H)
    r = random.choice([2, 2, 3, 4]) * SS
    g.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 200))

img = img.filter(ImageFilter.SMOOTH)

# ── 제목 ───────────────────────────────────────────────────────
def fnt(sz):
    try: return ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", sz)
    except Exception: return ImageFont.load_default()

# 제목 뒤를 어둡게 깔아 몬스터 위에서도 글자가 읽히게 한다.
shade = Image.new("RGBA", img.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
# ⚠ 처음에 알파를 뒤집어 넣어 **위가 진하고 아래가 맑은** 띠가 됐다.
#   화면 한복판에 가로줄이 생겨 그림이 두 동강 났다. 아래로 갈수록 진해야 한다.
for i in range(px(240)):
    a = int(205 * (1 - i / px(240)) ** 1.4)
    sd.line([0, H - i, W, H - i], fill=(10, 10, 22, a))
img = Image.alpha_composite(img.convert("RGBA"), shade)

g = ImageDraw.Draw(img)
title = "메이플 레벨업"
f = fnt(px(104))
tw = g.textlength(title, font=f)
tx, ty = W / 2 - tw / 2, H - px(168)
for ox in range(-px(7), px(8), px(2)):
    for oy in range(-px(7), px(8), px(2)):
        g.text((tx + ox, ty + oy), title, font=f, fill=(18, 18, 28))
g.text((tx, ty), title, font=f, fill=(255, 214, 66))

sub = "뺏은 기술로 한 방씩, 세계가 열린다"
f2 = fnt(px(34))
sw = g.textlength(sub, font=f2)
sx, sy = W / 2 - sw / 2, H - px(52)
for ox in (-px(3), px(3)):
    for oy in (-px(3), px(3)):
        g.text((sx + ox, sy + oy), sub, font=f2, fill=(16, 16, 26))
g.text((sx, sy), sub, font=f2, fill=(214, 228, 250))

out = img.convert("RGB").resize((1280, 720), Image.LANCZOS)
out.save(sys.argv[1])
print(sys.argv[1], out.size)
