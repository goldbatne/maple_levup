"""rect만으로 그린 SVG를 그대로 픽셀로 찍는다.

painter의 render.cjs는 puppeteer(약 200MB)를 요구하는데 스킬 폴더에
package-lock.json이 없어 `npm ci`가 실패한다. 이 그림은 <rect>밖에 안 쓰므로
직접 찍는 편이 싸고 결과도 같다 (보간 없음 = chunky 규칙 그대로).
"""
import re, sys
from PIL import Image

src, out, scale = sys.argv[1], sys.argv[2], int(sys.argv[3])

text = open(src, encoding='utf-8').read()
m = re.search(r'viewBox="0 0 (\d+) (\d+)"', text)
gw, gh = int(m.group(1)), int(m.group(2))

im = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
px = im.load()

n = 0
for tag in re.findall(r'<rect\b[^>]*>', text):
    def at(name, default=None):
        mm = re.search(name + r'="([^"]+)"', tag)
        return mm.group(1) if mm else default
    x = int(at('x', '0')); y = int(at('y', '0'))
    w = int(at('width', '1')); h = int(at('height', '1'))
    fill = at('fill', '#000000').lstrip('#')
    rgb = tuple(int(fill[i:i + 2], 16) for i in (0, 2, 4))
    for yy in range(y, min(y + h, gh)):
        for xx in range(x, min(x + w, gw)):
            if xx >= 0 and yy >= 0:
                px[xx, yy] = rgb + (255,)
    n += 1

im = im.resize((gw * scale, gh * scale), Image.NEAREST)
im.save(out)
print('rect ' + str(n) + '개 -> ' + out + ' ' + str(im.size))
