from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parents[1]
src=Path('C:/Users/dddd/.codex/generated_images/01a0955f-0d5b-7931-a751-c770b2046bd8/exec-4acd12e6-8463-47f5-b6c5-5a92eb3a470a.png')
dst=R/'source/F03_blue_matte.png'
if not dst.exists(): shutil.copy2(src,dst)
im=Image.open(dst).convert('RGB'); c=np.asarray(im).astype(float)/255
# Blue screen: assumed foreground blue = .65 * min(red, green).
# Invert C=alpha*F+(1-alpha)*[0,0,1]. This is an estimate, not recovered native alpha.
a=np.clip(1-c[:,:,2]+.65*np.minimum(c[:,:,0],c[:,:,1]),0,1)
a[a<3/255]=0
f=(c-(1-a[:,:,None])*np.array([0,0,1]))/np.maximum(a[:,:,None],1/255)
rgba=np.concatenate([np.clip(f,0,1),a[:,:,None]],axis=2)
o=Image.fromarray(np.rint(rgba*255).astype('uint8'),'RGBA').resize((384,384),Image.Resampling.LANCZOS)
p=R/'staging/CAST/003_m_mushroom_s_mon_mushroom_CAST_F03.png';p.parent.mkdir(parents=True,exist_ok=True);o.save(p)
board=Image.new('RGB',(1152,420));d=ImageDraw.Draw(board)
for i,bg in enumerate([0,128,255]):
 t=Image.new('RGBA',o.size,(bg,bg,bg,255));t.alpha_composite(o);board.paste(t.convert('RGB'),(i*384,36));d.text((i*384+8,8),'F03 / REVIEW ONLY / bg '+str(bg),fill='white')
board.save(R/'preview/F03_ALPHA_QA.png')
ar=np.asarray(o)[:,:,3]; report={'source':str(dst),'source_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'output':str(p),'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'alpha_min':int(ar.min()),'alpha_max':int(ar.max()),'transparent_pixels':int((ar==0).sum()),'partial_alpha_pixels':int(((ar>0)&(ar<255)).sum()),'source_background_corner_rgb':list(im.getpixel((0,0))),'alpha_method':'estimated blue-screen inversion; foreground blue=.65*min(red,green); noise cutoff3/255; full-canvas resize384; no recenter','art_gate':'PENDING_VISUAL_REVIEW','native_alpha_recovered':False}
(R/'records/F03_ALPHA.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
