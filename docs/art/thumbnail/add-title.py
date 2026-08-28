# 대표 이미지에 제목을 얹는다.
#
# 캐주얼 게임 로고의 세 겹 구조를 그대로 만든다:
#   1) 두께(extrude)  같은 글자를 아래로 여러 번 찍어 입체로 세운다
#   2) 테두리(outline) 글자 마스크를 부풀려 어두운 색으로 두른다
#   3) 앞면(face)      위는 밝은 노랑, 아래는 주황인 세로 그라데이션
#
# ⚠ 글자를 그냥 얹으면 배경이 복잡해서 안 읽힌다. 뒤에 어두운 빛무리를 깔아
#   글자 주변만 살짝 눌러 준다.
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]
OUT = sys.argv[2]
SUB = sys.argv[3] if len(sys.argv) > 3 else ""

im = Image.open(SRC).convert("RGBA")
W, H = im.size

def f(path, sz):
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.load_default()

TITLE = "메이플 레벨업"
FS = int(H * 0.155)
font = f("C:/Windows/Fonts/HMKMRHD.TTF", FS)      # 굵고 각진 한글
probe = ImageDraw.Draw(Image.new("L", (1, 1)))
tw = probe.textlength(TITLE, font=font)
if tw > W * 0.80:                                  # 너무 넓으면 줄인다
    FS = int(FS * (W * 0.80) / tw)
    font = f("C:/Windows/Fonts/HMKMRHD.TTF", FS)
    tw = probe.textlength(TITLE, font=font)

TX, TY = (W - tw) / 2, H * 0.045
def odd(v):
    # ImageFilter.MaxFilter는 **홀수 크기만** 받는다. 짝수를 넘기면 bad filter size.
    v = int(v)
    return v + 1 if v % 2 == 0 else max(3, v)
DEPTH, OUTW = max(4, int(FS * 0.10)), max(3, int(FS * 0.075))

def text_mask(dx=0, dy=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((TX + dx, TY + dy), TITLE, font=font, fill=255)
    return m

face = text_mask()

# 1) 뒤에 어두운 빛무리 — 배경이 복잡해도 글자가 읽히게
halo = face.filter(ImageFilter.MaxFilter(odd(OUTW * 4 + 1))).filter(ImageFilter.GaussianBlur(FS * 0.18))
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
lay.putalpha(halo.point(lambda v: int(v * 0.62)))
lay = Image.new("RGBA", (W, H), (12, 10, 20, 0))
lay.putalpha(halo.point(lambda v: int(v * 0.62)))
im = Image.alpha_composite(im, lay)

# 2) 두께 — 아래로 찍어 내려간다
for i in range(DEPTH, 0, -1):
    t = i / DEPTH
    col = (int(96 - 40 * t), int(52 - 22 * t), int(18 - 8 * t))
    m = text_mask(0, i).filter(ImageFilter.MaxFilter(odd(OUTW + 1)))
    l = Image.new("RGBA", (W, H), col + (255,)); l.putalpha(m)
    im = Image.alpha_composite(im, l)

# 3) 테두리
m = face.filter(ImageFilter.MaxFilter(odd(OUTW * 2 + 1)))
l = Image.new("RGBA", (W, H), (56, 30, 12, 255)); l.putalpha(m)
im = Image.alpha_composite(im, l)
m2 = face.filter(ImageFilter.MaxFilter(odd(OUTW)))
l = Image.new("RGBA", (W, H), (150, 92, 30, 255)); l.putalpha(m2)
im = Image.alpha_composite(im, l)

# 4) 앞면 — 세로 그라데이션
grad = Image.new("RGB", (1, H))
gd = ImageDraw.Draw(grad)
y0, y1 = TY, TY + FS * 1.25
for y in range(H):
    t = min(max((y - y0) / max(1, (y1 - y0)), 0), 1)
    gd.point((0, y), fill=(int(255 - 6 * t), int(236 - 62 * t), int(120 - 78 * t)))
grad = grad.resize((W, H))
l = grad.convert("RGBA"); l.putalpha(face)
im = Image.alpha_composite(im, l)

# 5) 윗면 하이라이트
hi = Image.new("L", (W, H), 0)
ImageDraw.Draw(hi).text((TX, TY - max(2, FS * 0.035)), TITLE, font=font, fill=255)
hi = Image.composite(hi, Image.new("L", (W, H), 0), face)
l = Image.new("RGBA", (W, H), (255, 252, 214, 255))
l.putalpha(hi.point(lambda v: int(v * 0.55)))
im = Image.alpha_composite(im, l)

# ── 부제 리본 ──────────────────────────────────────────────────
if SUB:
    fs2 = int(FS * 0.30)
    font2 = f("C:/Windows/Fonts/malgunbd.ttf", fs2)
    sw = probe.textlength(SUB, font=font2)
    bw, bh = sw + fs2 * 2.0, fs2 * 1.9
    bx, by = (W - bw) / 2, TY + FS * 1.24
    rib = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    rd.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(bh * 0.30),
                         fill=(58, 32, 14, 236), outline=(196, 140, 46, 255),
                         width=max(2, int(fs2 * 0.14)))
    im = Image.alpha_composite(im, rib)
    d = ImageDraw.Draw(im)
    d.text(((W - sw) / 2, by + (bh - fs2 * 1.32) / 2), SUB, font=font2, fill=(255, 232, 168))

im.convert("RGB").save(OUT, quality=95)
print(OUT, im.size, "글자크기", FS)
