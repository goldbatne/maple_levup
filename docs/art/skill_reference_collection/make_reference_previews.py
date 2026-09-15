from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).parent; refs=json.loads((root/'selected.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
atlas=Image.new('RGB',(1000,len(refs)*180),(45,45,45));draw=ImageDraw.Draw(atlas)
for row,r in enumerate(refs):
 d=root/'selected'/r['key'];frames=d/'frames';frames.mkdir(exist_ok=True)
 draw.text((8,row*180+4),r['key']+' / '+str(r['names'].get('ko',[])),font=font,fill='white')
 x=8
 for e in r['elements']:
  files=list(d.glob(e['ruid']+'.*'));assert files,(r['key'],e['ruid']);im=Image.open(files[0]);n=getattr(im,'n_frames',1);indices=sorted(set([0,n//3,2*n//3,n-1]))
  durations=[]
  for i in range(n):im.seek(i);durations.append(im.info.get('duration'))
  e['preview_frame_count']=n;e['preview_durations_ms']=durations;e['selected_frame_indices']=indices
  for i in indices:
   im.seek(i);a=im.convert('RGBA');a.save(frames/(e['ruid']+f'_F{i:03}.png'))
  im.seek(n//2);a=im.convert('RGBA');a.thumbnail((140,120));atlas.paste(a,(x,row*180+30),a);draw.text((x,row*180+152),e['rel_path'],font=font,fill='white');x+=155
(root/'selected.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf-8');atlas.save(root/'SELECTED_REFERENCE_ATLAS.jpg')
print(root/'SELECTED_REFERENCE_ATLAS.jpg')
