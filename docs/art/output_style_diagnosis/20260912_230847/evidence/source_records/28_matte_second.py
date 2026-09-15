from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,shutil,hashlib
R=Path(__file__).resolve().parents[1]
src=Path('C:/Users/dddd/.codex/generated_images/01a0955f-0d5b-7931-a751-c770b2046bd8/exec-e5e2757b-6053-4601-93ca-ecd7748921d9.png');dst=R/'source/F03_attempt02_magenta.png';shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB');c=np.asarray(im).astype(float)/255
# Magenta matte inversion with assumed foreground B=.68G. Estimated, not native alpha.
a=np.clip(1-c[:,:,2]+.68*c[:,:,1],0,1);a[a<3/255]=0
f=(c-(1-a[:,:,None])*np.array([1,0,1]))/np.maximum(a[:,:,None],1/255)
raw=Image.fromarray(np.rint(np.concatenate([np.clip(f,0,1),a[:,:,None]],2)*255).astype('uint8'),'RGBA')
raw.thumbnail((384,384),Image.Resampling.LANCZOS);o=Image.new('RGBA',(384,384));o.alpha_composite(raw,((384-raw.width)//2,(384-raw.height)//2))
p=R/'staging/attempt02/003_m_mushroom_s_mon_mushroom_CAST_F03.png';p.parent.mkdir(parents=True,exist_ok=True);o.save(p)
board=Image.new('RGB',(1152,450),(35,35,35));d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
d.text((12,8),'주황 버섯 / 포자 살포 / CAST F03 — 두 번째 시안, 미채택',font=font,fill='white')
for i,bg in enumerate([0,128,255]):
 t=Image.new('RGBA',(384,384),(bg,bg,bg,255));t.alpha_composite(o);board.paste(t.convert('RGB'),(384*i,50))
board.save(R/'preview/F03_ATTEMPT02_ALPHA_QA.png')
ar=np.asarray(o)[:,:,3];report={'alpha_min':int(ar.min()),'alpha_max':int(ar.max()),'transparent_pixels':int((ar==0).sum()),'partial_alpha_pixels':int(((ar>0)&(ar<255)).sum()),'method':'magenta inverse with assumed foreground B=.68G; cutoff3/255; proportional fit and centered padding from1536x1024 to384square','source_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':'REQUIRES_VISUAL_REVIEW'}
(R/'records/F03_ATTEMPT02_ALPHA.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report)
