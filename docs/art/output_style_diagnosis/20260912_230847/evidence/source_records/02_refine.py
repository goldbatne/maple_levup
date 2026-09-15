from pathlib import Path
import csv, json, hashlib, zipfile, shutil, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RUN=Path(__file__).resolve().parents[1]
ROOT=Path('D:/maplestory_levup')
AUDIT=ROOT/'docs/art/output_audit/runs/20260912_192803_area00_intent_quality_review'
PKG=RUN/'AREA_00_IMAGES_INPUT_IMAGES_OUTPUT'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
selected=json.loads((AUDIT/'SELECTION.json').read_text(encoding='utf-8-sig'))
for r in selected:
    assert SHA(Path(r['path']).read_bytes())==r['sha256']
z=zipfile.ZipFile(selected[1]['path']); iz=zipfile.ZipFile(selected[0]['path'])
assert z.testzip() is None and iz.testzip() is None
original={}
for n in z.namelist():
    if n.endswith('/') : continue
    rel=Path(*n.split('/')[1:]); dst=PKG/rel
    dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(z.read(n))
    original[str(rel).replace('\\','/')]=n
for n in iz.namelist():
    if n.endswith('/') : continue
    if n.endswith('MONSTER_IMAGE.png') or n.endswith('GENERATION_SPEC.md') or n.split('/')[-1] in ['OUTPUT_FORMAT_SPEC.md','OUTPUT_NAMING_SPEC.md','AREA_MANIFEST.md']:
        dst=RUN/'provenance/input'/Path(*n.split('/')[1:]);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(iz.read(n))
for n in ['SELECTION.json','REVIEW_SUMMARY.md','SAFE_AREA_REVIEW.csv','SOURCE_SCOPE.md']:
    dst=RUN/'provenance/review'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(AUDIT/n,dst)
dump(RUN/'provenance/BASELINE_IDENTITY.json',selected)
genroot=Path('C:/Users/dddd/.codex/generated_images/01a0955f-0d5b-7931-a751-c770b2046bd8')
gens={5:'exec-84821b6b-f34b-4b91-b804-05a5151a1a5c.png',6:'exec-ad765089-219e-4c04-855c-2e56f21f25cf.png',7:'exec-fc8630a4-a22b-429c-b24d-a75c15305b84.png'}
rawdir=RUN/'provenance/image_edits';rawdir.mkdir(parents=True,exist_ok=True)
for n,f in gens.items(): shutil.copy2(genroot/f,rawdir/f'F{n:02d}_raw_black.png')
shutil.copy2(genroot/'exec-4bdfc5e5-1d7f-461a-ab8a-632c3a567aaa.png',rawdir/'F05_REJECTED_baked_checkerboard.png')
mano=next((PKG/'monsters').glob('004*'))
shutil.copy2(next((mano/'PREVIEW').glob('*CONTACT*')),rawdir/'APPROVED_CONTACT_PREVIEW.png')

def prem(im):
    a=np.asarray(im.convert('RGBA'),dtype=np.float32)/255
    return a[:,:,:3]*a[:,:,3:4],a[:,:,3:4]
def rgba(rgb,a):
    return Image.fromarray(np.uint8(np.rint(np.clip(np.concatenate([np.divide(rgb,a,out=np.zeros_like(rgb),where=a>0),a],axis=2),0,1)*255)))
def black(im):
    rgb,_=prem(im);return Image.fromarray(np.uint8(np.rint(rgb*255)))
repairs={};records=[]
for n in [5,6,7]:
    src=Image.open(mano/f'VFX/004_m_mano_s_mon_mano_F{n:02d}.png').convert('RGBA')
    pad=Image.new('RGBA',(768,768));pad.paste(src,(128,128))
    target=np.asarray(black(pad),dtype=np.float32)
    raw=Image.open(rawdir/f'F{n:02d}_raw_black.png').convert('RGB').resize((768,768),Image.Resampling.LANCZOS)
    # Registration uses intact central artwork only, never centers frames independently.
    ys,xs=np.mgrid[335:580:5,235:565:5]; ref=target[ys,xs]
    weights=(ref.max(axis=2)>35).astype(float)[:,:,None]
    best=(1e30,None)
    for scale in np.arange(.96,1.041,.01):
        k=1/float(scale)
        arr=np.asarray(raw.transform((768,768),Image.Transform.AFFINE,(k,0,384*(1-k),0,k,384*(1-k)),Image.Resampling.BICUBIC),dtype=np.float32)
        for dx in range(-12,13,2):
            for dy in range(-12,13,2):
                score=float((((arr[ys-dy,xs-dx]-ref)**2)*weights).mean())
                if score<best[0]: best=(score,(float(scale),dx,dy))
    scale,dx,dy=best[1];k=1/scale
    aligned=raw.transform((768,768),Image.Transform.AFFINE,(k,0,384*(1-k)-dx*k,0,k,384*(1-k)-dy*k),Image.Resampling.BICUBIC)
    g=np.asarray(aligned,dtype=np.float32)/255
    # Black-composite unmatting is limited to luminous replacement edges.
    # Alpha follows max channel, continuous (no color-key deletion of highlights).
    ga=np.clip(g.max(axis=2,keepdims=True)/.97,0,1)
    ga[ga<3/255]=0;g=np.minimum(g,ga)
    op,oa=prem(pad)
    yy,xx=np.mgrid[0:768,0:768]
    left=np.clip((205-xx)/45,0,1) if n in [6,7] else np.zeros_like(xx,dtype=float)
    right=np.clip((xx-565)/45,0,1) if n in [5,6] else np.zeros_like(xx,dtype=float)
    vertical=np.minimum(np.clip((yy-365)/35,0,1),np.clip((620-yy)/35,0,1))
    mask=(np.maximum(left,right)*vertical)[:,:,None]
    out=rgba(op*(1-mask)+g*mask,oa*(1-mask)+ga*mask)
    out_arr=np.array(out); untouched=mask[:,:,0]==0
    out_arr[untouched]=np.asarray(pad)[untouched];out=Image.fromarray(out_arr)
    out.save(rawdir/f'F{n:02d}_repaired_expanded.png')
    Image.fromarray(np.uint8(mask[:,:,0]*255)).save(rawdir/f'F{n:02d}_edit_mask.png')
    aligned.save(rawdir/f'F{n:02d}_registered_black.png')
    repairs[n]=out
    records.append(dict(frame=f'F{n:02d}',method='참조 기반 원화 편집',raw_path=str(rawdir/f'F{n:02d}_raw_black.png'),raw_sha256=SHA((rawdir/f'F{n:02d}_raw_black.png').read_bytes()),registration_scale=scale,registration_dx=dx,registration_dy=dy,registration_mse=best[0],source_padding=128,source_canvas=512,working_canvas=768,core_original_pixels_preserved=bool(np.array_equal(np.asarray(out)[128:640,210:560],np.asarray(pad)[128:640,210:560]))))
dump(rawdir/'EDIT_RECORDS.json',records)
# Native-sized QA board; no frame is auto-centered.
board=Image.new('RGB',(1536,768),(35,39,45))
for i,n in enumerate([5,6,7]):
    im=repairs[n];im=im.resize((512,512),Image.Resampling.LANCZOS)
    for j,bg in enumerate([(0,0,0),(128,128,128),(255,255,255)]):
        # Full repair with original padded coordinates shown at half resolution.
        small=repairs[n].resize((256,256),Image.Resampling.LANCZOS)
        cell=Image.new('RGBA',(512,256),(*bg,255));cell.alpha_composite(small,(128,0));board.paste(cell.convert('RGB'),(i*512,j*256))
board.save(RUN/'work/REPAIR_QA.png')
print(json.dumps(records,ensure_ascii=False,indent=2))
