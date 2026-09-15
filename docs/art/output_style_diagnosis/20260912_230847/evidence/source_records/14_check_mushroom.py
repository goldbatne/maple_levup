from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,shutil,hashlib
R=Path(__file__).resolve().parents[1];dest=R/'staging/AREA_01/m_mushroom/CAST';dest.mkdir(parents=True,exist_ok=True)
sources=['exec-bee4f093-eae4-4157-889a-65282b1064a1.png','exec-4eee58d2-e65f-428a-8294-23c535240e43.png'];base=Path('C:/Users/dddd/.codex/generated_images/01a0955f-0d5b-7931-a751-c770b2046bd8')
for n,src in enumerate(sources,1):shutil.copy2(base/src,R/'evidence'/f'MUSHROOM_CAST_ATTEMPT{n}.png')
im=Image.open(base/sources[1]);a=np.array(im.convert('RGB'),dtype=float);lum=a.max(2)
# Uniform black matte extraction for this light powder effect only; preserve source RGB over black.
alpha=np.clip((lum-2)/126,0,1);rgb=np.clip((a-2)/np.maximum(alpha[:,:,None],1/255),0,255);rgba=Image.fromarray(np.dstack([rgb,alpha*255]).astype('uint8'),'RGBA')
rows=[];preview=Image.new('RGB',(1536,3*220),'#444');d=ImageDraw.Draw(preview);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',14)
for i in range(8):
 box=[round(i%4*im.width/4),round(i//4*im.height/2),round((i%4+1)*im.width/4),round((i//4+1)*im.height/2)]
 cell=rgba.crop(box);edge=np.array(cell.getchannel('A'));edge_max=int(max(edge[0].max(),edge[-1].max(),edge[:,0].max(),edge[:,-1].max()))
 cell=cell.resize((384,384),Image.Resampling.LANCZOS);p=dest/f'003_m_mushroom_s_mon_mushroom_CAST_F{i:02}.png';cell.save(p)
 for j,bg in enumerate(['#000','#777','#fff']):
  thumb=cell.resize((192,192),Image.Resampling.LANCZOS);tile=Image.new('RGBA',(192,192),bg);tile.alpha_composite(thumb);preview.paste(tile.convert('RGB'),(i*192,j*220));d.text((i*192+5,j*220+195),f'F{i:02} / .10s',font=font,fill='white')
 rows.append({'frame':i,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'split_box':box,'source_cell_edge_alpha_max':edge_max,'alpha_range':cell.getchannel('A').getextrema(),'canvas':cell.size,'status':'NOT_APPROVED'})
preview.save(R/'evidence/MUSHROOM_CAST_3_BACKGROUNDS.png');(R/'evidence/MUSHROOM_CAST_TECHNICAL.json').write_text(json.dumps({'method':'black matte alpha=clip((maxRGB-2)/126), RGB unpremultiply; no illustration changes, no autocrop/recenter. Not universal dark-material method.','files':rows},indent=2),encoding='utf-8');print(json.dumps(rows))
