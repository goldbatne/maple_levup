# 생성 이미지 가운데 캐릭터를 토벤머리로 갈아 끼운다.
#
# ⚠ 그냥 붙이면 오려 붙인 티가 난다. 확대해 보고 원인이 넷이었다:
#   1) **외곽선이 없다** — 배경의 버섯·달팽이는 전부 어두운 테두리를 둘렀는데
#      토벤만 맨 실루엣이라 혼자 그림에서 떠 있다. 이게 제일 컸다.
#   2) 알파를 128에서 딱 잘라 **가장자리가 거칠다**.
#   3) 색이 너무 매끄럽다 — 배경은 단수가 적은 픽셀 음영인데 토벤은 그라데이션.
#   4) 장면은 따뜻한 빛인데 토벤은 중성색이다.
import sys
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter, ImageChops

BG  = 'D:/maplestory_levup/docs/art/thumbnail/thumbnails2.jpg'
TOB = 'D:/maplestory_levup/docs/art/thumbnail/toben-clean.png'
OUT = sys.argv[1]
TH  = int(sys.argv[2]) if len(sys.argv) > 2 else 340
CXY = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (514, 332)

GRID    = 2          # 배경의 픽셀 덩어리 크기
OUTLINE = (34, 26, 30)
OW      = 3          # 외곽선 두께

bg = Image.open(BG).convert("RGBA")
tob = Image.open(TOB).convert("RGBA")
tob = tob.crop(tob.split()[3].getbbox())

k = TH / tob.height
w, h = max(1, int(tob.width * k)), TH
tob = tob.resize((w, h), Image.LANCZOS)

# 픽셀 결 맞추기 (배경 덩어리 크기에 맞춰 한 번 내렸다 올린다)
tob = tob.resize((max(1, w // GRID), max(1, h // GRID)), Image.LANCZOS)
tob = tob.resize((w, h), Image.NEAREST)

alpha = tob.split()[3].point(lambda v: 255 if v > 120 else 0)

# 색: 단수를 줄이고 따뜻하게 — 배경 팔레트에 맞춘다
rgb = tob.convert("RGB")
rgb = ImageEnhance.Color(rgb).enhance(1.25)
rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
r, g, b = rgb.split()
r = r.point(lambda v: min(255, int(v * 1.04 + 4)))     # 따뜻한 빛
b = b.point(lambda v: max(0, int(v * 0.96)))
rgb = Image.merge("RGB", (r, g, b))
rgb = rgb.quantize(colors=40, method=Image.MEDIANCUT).convert("RGB")
tob = Image.merge("RGBA", (*rgb.split(), alpha))

# ── 외곽선 ─────────────────────────────────────────────────────
# 알파를 부풀려 그 차이만큼을 어두운 색으로 채운다. 이게 없으면 그림에서 뜬다.
pad = OW * 2 + 2
big = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
a_big = Image.new("L", big.size, 0)
a_big.paste(alpha, (pad, pad))
grown = a_big.filter(ImageFilter.MaxFilter(OW * 2 + 1))
line = Image.new("RGBA", big.size, OUTLINE + (255,))
line.putalpha(grown)
big = Image.alpha_composite(big, line)
big.alpha_composite(tob, (pad, pad))

out = bg.copy()

# 발밑 그림자 — 없으면 잔디 위에 떠 있는 것처럼 보인다.
sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(sh)
sx, sy = CXY[0], CXY[1] + h // 2 - int(h * 0.05)
sd.ellipse([sx - w * 0.30, sy - h * 0.035, sx + w * 0.30, sy + h * 0.035],
           fill=(18, 30, 14, 130))
sh = sh.filter(ImageFilter.GaussianBlur(7))
out = Image.alpha_composite(out, sh)

out.alpha_composite(big, (CXY[0] - big.width // 2, CXY[1] - big.height // 2))
out.convert("RGB").save(OUT, quality=95)
print(OUT, out.size, 'toben', (w, h), 'at', CXY)
