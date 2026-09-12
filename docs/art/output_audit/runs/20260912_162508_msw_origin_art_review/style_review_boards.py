from review_audit import *
from collections import defaultdict
OUT=RUN/'CROSS_AREA_STYLE_BOARD';OUT.mkdir(exist_ok=True);(RUN/'STYLE_OUTLIERS').mkdir(exist_ok=True)
FONT=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);SMALL=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
def rawpaste(c,data,x,y,w,h):
    im=Image.open(io.BytesIO(data)).convert('RGBA');assert im.width<=w and im.height<=h
    c.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2),im)
def main():
    rs=json.loads((RUN/'records.json').read_text('utf8'));bl=readcsv(ART/'output_audit/BASELINE_INDEX.csv');zp=next(r['path'] for r in bl if r['kind']=='AREA00_OUTPUT');z=zipfile.ZipFile(zp)
    bas={}
    for folder in sorted(set(n.split('/ICON/')[0] for n in z.namelist() if '/ICON/' in n and n.endswith('.png'))):
        key=folder.split('/')[-1].split('_',1)[1];ns=sorted(n for n in z.namelist() if n.startswith(folder+'/') and n.endswith('.png') and ('/ICON/' in n or '/VFX/' in n));bas[key]={'ICON':[n for n in ns if '/ICON/' in n],'CAST_VFX':[n for n in ns if '/VFX/' in n]}
    # Fix actual package selection: AREA12 latest package has identical art bytes, current canonical paths.
    latest=ART/'output_repacked/20260912_165951_area11_12_final/AREA_12_IMAGES_OUTPUT_V2_4_FINAL_CANDIDATE.zip'
    if latest.exists():
        oz=zipfile.ZipFile(latest);nm=next(n for n in oz.namelist() if n.endswith('OUTPUT_MANIFEST.csv'));prefix=nm[:-len('OUTPUT_MANIFEST.csv')];mf=zcsv(oz,nm)
        for r in rs:
            if r['area_id']!='area_12':continue
            r['output_zip']=str(latest);oldhashes=sorted(r['file_hashes'].values());r['role_files']={role:[prefix+p['relative_path'] for p in mf if p['monster_id']==r['monster_id'] and p['effect_role']==role] for role in r['role_files']};r['file_hashes']={n:hashlib.sha256(oz.read(n)).hexdigest() for ns in r['role_files'].values() for n in ns};assert sorted(r['file_hashes'].values())==oldhashes
    dump('STYLE_SELECTED_RECORDS.json',rs);dump('STYLE_AREA00_FILES.json',{'zip':zp,'files':bas})
    index=[]
    # Native-resolution baseline sequences, with the ICON beside the first row.
    for key,roles in bas.items():
        ns=roles['CAST_VFX'];sz=Image.open(io.BytesIO(z.read(ns[0]))).width;cols=4;c=Image.new('RGB',(sz*5,(sz+34)*((len(ns)+3)//4)+80),(32,38,48));d=ImageDraw.Draw(c);d.text((10,10),'AREA00 APPROVED / '+key+' / 1 image pixel = 1 board pixel',font=FONT,fill='white');rawpaste(c,z.read(roles['ICON'][0]),0,70,sz,sz)
        for j,n in enumerate(ns):x=(1+j%4)*sz;y=70+(j//4)*(sz+34);rawpaste(c,z.read(n),x,y,sz,sz);d.text((x+8,y+sz),f'F{j:02}',font=SMALL,fill='white')
        p=OUT/f'BASELINE_{key}.png';c.save(p);index.append({'board':str(p),'type':'AREA00_NATIVE_ALL_FRAMES','entries':key,'scale':'1:1','files':'|'.join(roles['ICON']+ns)})
    # Icon Area boards: all five approved icons and every actual Area icon at exact 256px.
    for area in sorted(set(r['area_id'] for r in rs)):
        selected=[r for r in rs if r['area_id']==area];nr=(len(selected)+4)//5;c=Image.new('RGB',(1400,360+nr*345),(32,38,48));d=ImageDraw.Draw(c);d.text((10,8),area+' ICON / native 256px / AREA00 baseline in top row',font=FONT,fill='white')
        for i,(key,rr) in enumerate(bas.items()):rawpaste(c,z.read(rr['ICON'][0]),i*280,40,256,256);d.text((i*280+6,300),key.split('_',2)[1],font=SMALL,fill='#ffdd99')
        for i,r in enumerate(selected):
            zz=zipfile.ZipFile(r['output_zip']);n=r['role_files']['ICON'][0];x=(i%5)*280;y=350+(i//5)*345;rawpaste(c,zz.read(n),x,y,256,256);d.text((x+4,y+263),r['monster_id'],font=SMALL,fill='white');d.text((x+4,y+288),r['skill_name'],font=SMALL,fill='white')
        p=OUT/f'{area}_ICON_NATIVE.png';c.save(p);index.append({'board':str(p),'type':'ICON_WITH_AREA00','entries':'|'.join(r['monster_id'] for r in selected),'scale':'1:1; no crop','files':'|'.join(r['role_files']['ICON'][0] for r in selected)})
    # Each non-icon role contains ALL actual frames at native pixels. Left column is a same-canvas AREA00 material reference.
    for r in rs:
        zz=zipfile.ZipFile(r['output_zip'])
        for role,ns in r['role_files'].items():
            if role=='ICON':continue
            sz=Image.open(io.BytesIO(zz.read(ns[0]))).width
            bk=next(k for k in bas if ('mano' in k if sz==512 else 'blue_snail' in k if sz==256 else 'red_snail' in k))
            # Material-specific alternative for wet, airy or translucent 384px effects.
            if sz==384 and r['monster_id'] in ['m_snail','m_mushroom','m_slime','m_fairy','m_octopus','m_jr_wraith','m_king_clang','m_white_fang','m_squid','m_shark','m_homun','m_roid','m_official_knight_c','m_mecateon','m_chronos']:bk=next(k for k in bas if 'slime' in k)
            bn=bas[bk]['CAST_VFX'];nrows=(len(ns)+3)//4;c=Image.new('RGB',(5*sz,(sz+34)*nrows+125),(32,38,48));d=ImageDraw.Draw(c)
            d.text((8,5),r['area_id']+' / '+r['monster_id']+' / '+r['skill_name']+' / '+role,font=FONT,fill='#ffe0a0');d.text((8,35),'1:1 native pixels · left: AREA00 '+bk+' · remaining cells: actual delivered F00..end',font=SMALL,fill='white');d.text((8,59),'Same background and pixel scale; different shapes, density and timing are allowed by each role contract.',font=SMALL,fill='#b7c3d7')
            for row in range(nrows):
                fi=[max(0,len(bn)//4),len(bn)//2,len(bn)-1][min(row,2)];y=95+row*(sz+34);rawpaste(c,z.read(bn[fi]),0,y,sz,sz);d.text((6,y+sz),'AREA00 F'+str(fi).zfill(2),font=SMALL,fill='#ffdd99')
            for j,n in enumerate(ns):x=(1+j%4)*sz;y=95+(j//4)*(sz+34);rawpaste(c,zz.read(n),x,y,sz,sz);d.text((x+8,y+sz),f'F{j:02}',font=SMALL,fill='white')
            p=OUT/f'{r["area_id"]}_{r["monster_id"]}_{role}_NATIVE.png';c.save(p);index.append({'board':str(p),'type':role+'_WITH_AREA00','entries':r['monster_id'],'scale':'1:1; no crop','files':'|'.join(ns),'baseline':bk})
    # Normalize index columns without dropping full filenames.
    for i in index:i.setdefault('baseline','five approved AREA00 icons' if i['type']=='ICON_WITH_AREA00' else '')
    writecsv('CROSS_AREA_STYLE_BOARD_INDEX.csv',index)
    print('BOARDS',len(index),'roles',sum(len(r['role_files']) for r in rs),'PNGs',sum(len(r['file_hashes']) for r in rs))
if __name__=='__main__':main()
