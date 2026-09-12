from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv, json, hashlib, zipfile, io, re, html, math
import numpy as np

P=Path(__file__).parent
R=json.loads((P/'RECORDS.json').read_text(encoding='utf-8'))
S=json.loads((P/'SELECTION.json').read_text(encoding='utf-8'))
REF=list(csv.DictReader((P/'REFERENCE_INVENTORY.csv').open(encoding='utf-8-sig')))
RF={int(x['index']):x for x in REF}
BG=(32,38,48,255)
F=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
H=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',25)
SM=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
def writecsv(name, rows):
    with (P/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def txt(d,x,y,t,width,font=F,color='white'):
    line='';step=font.size+8
    for c in t:
        if c=='\n' or d.textlength(line+c,font=font)>width:
            d.text((x,y),line,font=font,fill=color);line='' if c=='\n' else c;y+=step
        else:line+=c
    if line:d.text((x,y),line,font=font,fill=color);y+=step
    return y
def pic(path):return Image.open(path).convert('RGBA')
def local(r,n):return P/'sources'/r['monster_id']/Path(n).name
def e(t):return html.escape(str(t))
def rel(p):return Path(p).relative_to(P).as_posix()

D={
'm_snail':dict(
 req='이슬 청록을 주색, 연두를 코어·잔상·소수 입자로 사용. 낮은 점액 띠가 오른쪽으로 늘어나며 물방울이 뒤따라 소멸. 다중 접촉광. 중간 규모 1.2~2배. 8×384² / 약 100ms. ICON: 큰 이슬방울+낮은 꼬리.',
 implemented='F00~F03 낮은 띠의 연장, F04~F05 말림과 접촉성 섬광, F06 분절이 보인다. 둥근 물방울·점액 소재와 ICON의 큰 방울/꼬리가 대응한다. 균일 확대·축소만으로 만든 흐름은 아니다.',
 changed='F03~F05의 연두·황백 강조가 강해 주색 청록보다 연두가 먼저 읽힐 수 있다. 다중 대상별 접촉광은 실제 대상·런타임 없이 구현 완료로 단정할 수 없다. F07은 줄어든 띠와 단단한 물방울이 남아 one-shot 종료 인상이 별도 판단 대상이다.',
 finish='프로젝트 참고 #095의 어두운 청록 외곽·황백 리본·둥근 광택 방울과 가깝다. #178의 넓은 흰 흐름/푸른 반투명 겹과도 층 구분이 통한다. OUTPUT은 더 둥근 구슬과 매끈한 젤 광택에 무게를 둔다. #095는 독립적인 공식 최신 품질 근거가 아니다.',
 taste='청록 중심 문구와 연두가 강한 기존 #095 참고 사이에서 색 비중을 결정할 필요가 있다. 낮은 점액보다 보석/유리처럼 반짝이는 해석 및 마지막 방울의 잔존감을 유지할지 판단한다. 색이나 잔존량만으로 수정 확정하지 않는다.',
 refs=[95,178],peak=5,status='NEEDS_USER_REVIEW',motion='흐름·말림·분절 구현 / 종료 잔존감 판단',icon='큰 방울과 오른쪽 꼬리가 64px에서도 식별됨. VFX와 색·광택·물방울 형태가 연결됨.'),
'm_blue_snail':dict(
 req='푸른 껍질 결을 겹친 반원 보호막과 짧은 반사광. 발밑~몸통 중심에서 아래→위로 감싸고 한 번 맥동한 뒤 같은 중심에서 소멸. 0.8~1.2배. 8×256² / 약 100ms. ICON: 푸른 껍질 아치+흰 반사광.',
 implemented='F00~F02 열린 낮은 곡선이 올라오고 F03~F05 돔·나선 보호막을 이룬 뒤 F06~F07 분해된다. 닫힌 자기 보호 형태와 파랑/백청 반사광이 읽힌다. ICON의 나선 껍질이 VFX의 돔·나선과 연결된다.',
 changed='VFX는 단단한 껍질 판보다 물막·액체 곡선에 가깝고 ICON은 더 단단하고 매끈한 구체 껍질이다. 결 모티브는 있으므로 소재 누락으로 단정하지 않는다. 마지막 곡선과 방울의 밝은 잔존감은 종료 인상 확인 대상이다.',
 finish='#178의 푸른 반투명 층과 흰 곡선이 실질적인 보조 비교점이다. #100은 밝은 중심/유색 외곽의 층 구분만 비교 가능하며 각진 수정 판의 재질을 껍질에 강요할 수 없다. 기존 프로젝트 ICON #094의 픽셀·짙은 경계보다 새 ICON은 부드러운 그라데이션과 넓은 흰 반사면을 쓴다.',
 taste='단단한 방어 껍질을 물 같은 보호막으로 번역한 정도, ICON과 VFX의 고체/액체 차이를 허용할지 판단한다. 고정 중심의 정확한 게임 부착점은 미확인이다.',
 refs=[178,100,94],peak=4,status='NEEDS_USER_REVIEW',motion='아래→위 형성·맥동·분해 구현 / 재질과 종료 인상 판단',icon='푸른 나선과 아치 반사가 64px에서 읽힘. 윤곽은 VFX보다 단단하고 반사면이 넓음.'),
'm_red_snail':dict(
 req='적색 껍질 원반을 앞으로 압축하고 오른쪽 돌진 잔상→앞쪽 충돌→분산 소멸. 주 적색/보조 주황. 타격광은 대상 중심을 가리지 않는 외곽 중심. 소형 0.7~1.1배. 8×256² / 약 100ms. ICON: 원반+속도선.',
 implemented='F00~F03 적색 나선 원반과 왼쪽 잔상으로 오른쪽 추진을 표현한다. F04~F05 앞쪽 섬광, F06 곡선 조각, F07 작은 잔여 입자로 변한다. ICON의 원반·속도선·전방 타격광도 같은 동작을 요약한다.',
 changed='확정적인 핵심 소재·방향 누락은 관찰되지 않았다. 충돌광이 실제 대상 중심을 가리지 않는지, 시전자의 실제 돌진과 중복 이동하는지는 정지 납품물만으로 검증할 수 없다. F03 왼쪽 끝 희박한 알파 접촉은 마노의 강한 파형 절단과 같은 수준으로 분류하지 않았다.',
 finish='#067의 날카로운 밝기 전환/가늘어진 에너지 선, #084의 주황 섬광과 연무 분리와 비교했다. OUTPUT은 검은 연기·기계 부분을 복제하지 않고 붉은 둥근 껍질과 매끈한 불빛 잔상으로 번역한다. ICON의 선명한 외곽과 VFX의 부드러운 잔상 차이는 역할상 설명 가능하다.',
 taste='껍질이 불꽃성 에너지처럼 보이는 주황 외곽 강도를 유지할지는 취향 영역이다. INPUT이 주황 타격광을 허용하므로 화염 기능을 추가했다고 단정하지 않는다.',
 refs=[67,84],peak=3,status='NO_OBVIOUS_ISSUE',motion='압축·추진 잔상·전방 충돌·파편화가 가장 명료한 편',icon='64px에서 원반, 나선, 오른쪽 타격 방향이 남음. VFX와 색과 재질의 중심이 연결됨.'),
'm_mano':dict(
 req='진주빛 껍질 고리와 낮은 무지개 파동. 지면 중심에서 방사형/상향 발현 후 바깥 입자로 소멸. 중앙 타격광과 외곽 경계 분리. 보스 2~3배 허용. 안전영역 핵심 70%, 외곽 85%. 12×512² / 약 80ms. ICON: 진주 껍질 고리+무지개 파문.',
 implemented='진주 구슬, 부채꼴 껍질 결, 청록·분홍의 낮은 타원 파동이 F00~F07에서 형성된다. F06의 상향 빛은 명세의 상향 발현 허용 범위다. F08~F11은 고리 분절과 축소를 보인다. ICON과 VFX의 진주·껍질·파문이 잘 연결된다.',
 changed='F05 오른쪽, F06 양쪽, F07 왼쪽의 밝은 파형이 캔버스 경계에 닿아 잘린다. 85% 안전영역도 벗어난다. 이는 보스 규모 허용과 별개인 구체적 파일/배치 결함이다. F03→F04에서 지면 고리와 중심이 위로 옮겨 읽히며 고정 지면 중심과의 관계를 확인해야 한다. F11에도 구슬·별·큰 고리 조각이 남는다.',
 finish='#100/#101의 유색 층·흰 중심·외곽 무늬와 밝기 층 구분은 통한다. OUTPUT은 평면 수정판의 각진 분할 대신 진주·조개에 맞는 곡면 반사와 연속 무지개를 쓴다. #095의 둥근 광택과도 이어진다. 보스의 더 많은 층과 높은 밀도 자체는 마감 이탈이 아니다.',
 taste='조개/장신구 같은 진주 표현과 매우 밝은 중앙광이 의도한 마노 스킬로 적절한지 판단한다. F03→F04 위치 변화가 연출인지 중심 흔들림인지 확인할 필요가 있다. 경계 잘림은 이 취향 판단과 분리해 수정 후보로 남긴다.',
 refs=[100,101],peak=6,status='SPEC_MISMATCH',motion='파동 형성·분해 구현 / F05~F07 절단 확정 / 중심·종료 인상 판단',icon='64px에서 진주·껍질·고리의 큰 구조는 읽히지만 작은 방울과 별은 합쳐짐. 보스의 높은 밀도 허용 범위, 재생성 확정 근거 아님.'),
'm_slime':dict(
 req='탄성 점액 방울과 눌렸다 튀는 젤리 테두리. 몸통~발밑 동일 중심에서 한 번 확장·수축, 가로질러 이동하지 않음. 초록/연민트. 소형 0.7~1.1배. 8×256² / 약 100ms. ICON: 점액 방울+탄성 곡선.',
 implemented='F00~F03 젤 덩어리가 퍼지고 팔처럼 휘는 점액 가장자리가 나온다. F04 별 모양 발현 뒤 F05~F06 구체·곡선으로 재조립/수축한다. 눈·입 등 몬스터 본체는 없다. ICON의 늘어나는 초록 방울이 탄성 소재를 요약한다.',
 changed='F07이 작은 온전한 젤 덩어리로 돌아가므로 분해되어 사라짐보다 복원·반복 시작처럼 읽힐 수 있다. 전체 알파 면적은 절정보다 줄어들어 fade가 전혀 없다고 할 수는 없다. 비어 있는 마지막 프레임을 요구하지 않는다.',
 finish='#095 프로젝트 이슬의 둥근 반사 방울과 광택 리본이 가장 직접적인 마감 비교점이다. #035의 안개성 반투명은 다른 재질의 예이며 슬라임을 흐린 연기로 만들 기준이 아니다. 프로젝트 옛 ICON #092보다 새 ICON은 명암이 연속적이고 유리처럼 광택이 강하다.',
 taste='끈적한 젤리보다 보석 같은 유동 방울에 가까운 광택, 폭발 후 온전한 덩어리로 복원되는 종료 인상을 유지할지 판단한다. 명시된 탄성 확장·수축은 있어 동작 전체 누락으로 분류하지 않는다.',
 refs=[95,35,92],peak=4,status='NEEDS_USER_REVIEW',motion='눌림·퍼짐·반동 구현 / one-shot 끝의 덩어리 복원 인상 판단',icon='64px에서 큰 방울과 늘어나는 꼬리가 선명하다. VFX와 광택·색이 같으나 VFX는 퍼진 젤리, ICON은 잡아 늘린 방울로 역할을 요약함.')
}

qual=[]
native_notes={35:('VFX_STATIC','보라 안개·얇은 지면 타원. 흐린 재질의 예; 선명한 외곽선이나 동작 타이밍 증거 아님.'),67:('VFX_STATIC','보라 세로 에너지의 날카로운 선과 어두운 중심. 정지 프레임 마감만 사용.'),84:('MIXED_VFX_OBJECT','주황 타격광/검은 연기/기계가 혼합. 섬광과 연기 분리만 사용; 기계·기능 복제 금지.'),92:('PROJECT_ICON','프로젝트 직접 제작 기록의 옛 점액 ICON. 픽셀 실루엣 비교만; 공식 최신 VFX 기준 아님.'),94:('PROJECT_ICON','프로젝트 직접 제작 기록의 옛 껍질 ICON. 픽셀 실루엣 비교만; 공식 최신 VFX 기준 아님.'),95:('PROJECT_VFX_STATIC','같은 이슬 스킬의 기존 프로젝트 참고. 둥근 광택/리본 표현의 당초 참고로 사용. 독립적인 최신 공식 품질 또는 AREA00 전체 성공의 근거로 사용하지 않음.'),100:('VFX_STATIC','수정 같은 판과 밝은 수평 중심, 가는 외곽 무늬. 층 구분 비교만; 모양·재질 강제 금지.'),101:('VFX_STATIC','보라 수정 판과 흰 중심. 층 구분 비교만; 모양·재질 강제 금지.'),178:('VFX_STATIC','푸른 회오리의 흰 리본과 반투명 겹. 흐름의 정지 표현 참고; 전체 애니메이션 미확보.'),180:('MIXED_VFX_OBJECT','검은 몸체성 대상+청록 검광/수평 잔상. 순수 VFX 기준에서 제외하고 혼합 자료 사례로만 확인.')}
for x in REF:
    i=int(x['index']);kind,note=native_notes.get(i,('CONTACT_SHEET_SCREENED_ONLY','183개 인벤토리 축소 보드에서 내용 선별만 수행. 정밀 마감/알파/동작 판단 근거로 사용하지 않음.'))
    if i in [77,128,142]:kind='BLANK_OR_NEAR_BLANK_SCREENED';note='제공 썸네일에서 유효한 형상 식별이 어려움. 품질/소멸 기준으로 사용하지 않음.'
    if i in [7,20,48,53,96,107,118,141,150,161,173,182]:kind='BODY_SCREENED';note='본체 이미지가 중심. 몬스터 정체성 보조 외 VFX 마감 근거로 사용하지 않음.'
    qual.append(dict(index=i,name=x['skill_resource_name'],RUID=x['RUID'],original_priority=x['style_priority'],chronology=x['known_era_version_date'],view_scope='NATIVE_1_TO_1' if i in native_notes else 'INVENTORY_ONLY',usable_kind=kind,use_limitation=note,zip_member=x['zip_member'],sha256=x['sha256']))
writecsv('REFERENCE_QUALIFICATION.csv',qual)

measure=[];review=[];evidence=[];crop_index=[]
for r in R:
    mid=r['monster_id'];v=D[mid];folder=P/'evidence'/mid;folder.mkdir(exist_ok=True)
    expected=512 if mid=='m_mano' else 384 if mid=='m_snail' else 256
    dt=80 if mid=='m_mano' else 100
    paths=[local(r,n) for n in r['vfx_files']];frames=[pic(p) for p in paths]
    sums=[int(np.asarray(im)[:,:,3].sum()) for im in frames]
    for i,(n,im) in enumerate(zip(r['vfx_files'],frames)):
        a=np.asarray(im)[:,:,3];edge=np.concatenate((a[0],a[-1],a[:,0],a[:,-1]));yy,xx=np.where(a>16)
        w,h=im.size;out=((xx<.075*w)|(xx>=.925*w)|(yy<.075*h)|(yy>=.925*h)).sum()
        measure.append(dict(monster_id=mid,frame=f'F{i:02}',file=n,width=w,height=h,required_width=expected,required_height=expected,canvas_match=im.size==(expected,expected),rgba=True,alpha_min=int(a.min()),alpha_max=int(a.max()),edge_alpha_max=int(edge.max()),edge_pixels_over16=int((edge>16).sum()),outside_centered85_pixels_alpha_over16=int(out),alpha_sum=sums[i],alpha_sum_vs_peak=round(sums[i]/max(sums),4),interpretation='외곽 85%는 중앙 정렬 사각형으로 계산한 보조 측정. 흐림/입자와 핵심 형태를 자동 분류하지 않음. 알파 합은 밝기나 품질 점수 아님.'))
    # Context page: original monster / requirements / actual icon / exact available references.
    b=Image.new('RGBA',(1100,1110),BG);d=ImageDraw.Draw(b)
    txt(d,20,14,f"AREA 00 · {r['monster_name']} / {r['skill_name']}",1060,H)
    txt(d,20,55,'원본 파일 픽셀 1:1 · 게임 표시 크기 아님 · 승인 여부를 품질 근거로 사용하지 않음',1060,SM)
    b.alpha_composite(pic(P/'sources'/mid/'MONSTER_IMAGE.png'),(20,120));b.alpha_composite(pic(local(r,r['icon_file'])),(390,110))
    b.alpha_composite(pic(local(r,r['icon_file'])).resize((64,64),Image.Resampling.LANCZOS),(740,180))
    txt(d,20,85,'INPUT MONSTER_IMAGE 320×240',340,SM);txt(d,390,85,'실제 OUTPUT ICON 256×256',300,SM);txt(d,720,140,'ICON 64px 가독성',240,SM)
    txt(d,20,374,'RUID: '+r['monster_image_ruid']+' / INPUT 수록 사본 · 이번 실시간 MSW 조회 없음',1060,SM)
    txt(d,20,413,'INPUT 핵심 요구',1060,H);txt(d,20,452,v['req'],1050)
    yy=572
    txt(d,20,yy,'사용 가능한 실제 INPUT 참고 / 원본 픽셀 1:1',1060,H)
    for j,idx in enumerate(v['refs']):
        x=20+j*355;im=pic(P/'sources'/f'ref_{idx:03}.png');b.alpha_composite(im,(x,655))
        txt(d,x,612,f"#{idx:03} {RF[idx]['style_priority']}",335,SM)
        txt(d,x,905,native_notes[idx][1],335,SM)
    txt(d,20,1055,'다음: 동일 파일의 전체 프레임 → 2배 상세 비교. 참고의 출시 시기·전체 재생 리듬은 미확인.',1060,SM)
    context=folder/'01_CONTEXT.png';b.convert('RGB').save(context)
    pages=[context]
    # Clearly separated complete native frame panels; no resize, crop, recenter or frame interpolation.
    for start in range(0,len(frames),4):
        size=frames[0].width;cw=size+28;width=max(700,cw*2+20);height=100+(size+54)*2
        b=Image.new('RGBA',(width,height),BG);d=ImageDraw.Draw(b)
        txt(d,15,10,f'{r["monster_name"]} / 모든 납품 VFX / 1:1',width-30,H)
        txt(d,15,48,f'캔버스 {size}×{size} · 순서 F00→F{len(frames)-1:02} · INPUT 약 {dt}ms/프레임',width-30,SM)
        for j,i in enumerate(range(start,min(start+4,len(frames)))):
            x=16+(j%2)*cw;y=90+(j//2)*(size+54);d.text((x,y),f'F{i:02}',font=F,fill='#ffce7d');b.alpha_composite(frames[i],(x,y+28))
        target=folder/f'02_FRAMES_{start:02}_{min(start+3,len(frames)-1):02}.png';b.convert('RGB').save(target);pages.append(target)
    # 2x nearest-neighbour detail is explicit; preserves source pixel values, not invented detail.
    b=Image.new('RGBA',(1100,800),BG);d=ImageDraw.Draw(b)
    txt(d,20,15,f'{r["monster_name"]} / 동일 2배 배율 상세 · 최근접 이웃 확대',1060,H)
    samples=[('참고 '+str(v['refs'][0]),P/'sources'/f"ref_{v['refs'][0]:03}.png",None),('실제 VFX '+f"F{v['peak']:02}",paths[v['peak']],None),('실제 ICON',local(r,r['icon_file']),None)]
    for j,(label,path,_) in enumerate(samples):
        im=pic(path);aa=np.asarray(im);mask=aa[:,:,3]>32
        if path.name.startswith('ref_') and int(path.stem[-3:])!=95:
            mask=mask & (aa[:,:,:3].min(axis=2)<200)
        ys,xs=np.where(mask);cx=int((xs.min()+xs.max())/2);cy=int((ys.min()+ys.max())/2)
        left=max(0,min(im.width-128,cx-64));top=max(0,min(im.height-128,cy-64));box=(left,top,left+128,top+128)
        crop=im.crop(box).resize((256,256),Image.Resampling.NEAREST);x=20+j*355
        txt(d,x,70,label,330);b.alpha_composite(crop,(x,115));txt(d,x,389,f'원본 crop {box}\n128² → 256² (2×)',330,SM)
        crop_index.append(dict(monster_id=mid,label=label,source=rel(path),box=json.dumps(box),scale=2,resampling='NEAREST'))
    txt(d,20,466,'마감 대조',1060,H);txt(d,20,509,v['finish'],1050)
    txt(d,20,650,'비교 한계: 참고가 흰 배경에 합성된 썸네일이면 원본 알파 가장자리 품질을 직접 비교할 수 없다. 확대는 생성/복원/샤프닝이 아니다.',1050,SM)
    zoom=folder/'03_FINISH_ZOOM_2X.png';b.convert('RGB').save(zoom);pages.append(zoom)
    # A full board is a convenient original-resolution document, with separate pages for comfortable native viewing.
    ims=[pic(q) for q in pages];full=Image.new('RGB',(max(q.width for q in ims),sum(q.height for q in ims)),BG[:3]);y=0
    for im in ims:full.paste(im.convert('RGB'),(0,y));y+=im.height
    fullpath=folder/'FULL_COMPARISON.png';full.save(fullpath)
    evidence.append(dict(monster_id=mid,skill_id=r['skill_id'],context=rel(context),all_frames=';'.join(rel(q) for q in pages if 'FRAMES' in q.name),zoom=rel(zoom),full_comparison=rel(fullpath),scope='실제 5 ICON/44 VFX 전체 정지 프레임 관찰; 재생 뷰어는 INPUT 타이밍 가정의 검수용'))
    for role,files in [('VFX',r['vfx_files']),('ICON',[r['icon_file']])]:
        review.append(dict(area='area_00',monster_id=mid,monster_name=r['monster_name'],skill_id=r['skill_id'],role=role,files=';'.join(files),input_spec='AREA_00_IMAGES_INPUT/'+r['folder']+'/GENERATION_SPEC.md',core_requirement=v['req'],implemented=v['implemented'] if role=='VFX' else v['icon'],difference=v['changed'] if role=='VFX' else 'VFX보다 선명한 외곽/넓은 반사면. 소재·실루엣 대응은 확인. 사용자 최종 품질 승인을 뜻하지 않음.',spec_result=v['status'] if role=='VFX' else 'NO_OBVIOUS_ISSUE',style_result='NEEDS_USER_REVIEW',reference_files=';'.join(RF[i]['zip_member'] for i in v['refs']),finish_observation=v['finish'],taste_decision=v['taste'],user_approved=False,game_scale_verified=False,evidence=rel(fullpath)))
    r['review']=v;r['dt_ms']=dt;r['native_files']=[rel(q) for q in paths];r['native_icon']=rel(local(r,r['icon_file']));r['pages']=[rel(q) for q in pages]

writecsv('FRAME_MEASUREMENTS.csv',measure);writecsv('ART_REVIEW.csv',review);writecsv('EVIDENCE_INDEX.csv',evidence);writecsv('ZOOM_CROP_INDEX.csv',crop_index)

# The visible horizontal span alone can exceed 85%, regardless of how the safe box is anchored.
# A>=128 is only a conservative way to exclude very faint glow; it is not a new asset requirement.
safe=[]
for r in R:
    for i,n in enumerate(r['vfx_files']):
        im=pic(local(r,n));a=np.asarray(im)[:,:,3];yy,xx=np.where(a>=128)
        if len(xx) and (xx.max()+1-xx.min())/im.width>.85:
            safe.append(dict(monster_id=r['monster_id'],skill_id=r['skill_id'],frame=f'F{i:02}',file=n,visible_span_px=int(xx.max()+1-xx.min()),canvas_width=im.width,visible_span_ratio=round(float((xx.max()+1-xx.min())/im.width),4),requirement='GENERATION_SPEC: 외곽 파편은 캔버스 안전영역85%를 넘지 않음',judgment='SPEC_MISMATCH_SAFE_MARGIN',method='A>=128 가시 영역의 가로폭만으로85% 초과. 희박한 glow 제외를 위한 보수적 증거이며 품질 점수/새 알파 조건 아님.',action='기술적 여백/배치 보정 후보. 본체 절단이 있으면 원화 복구와 별도 연결. 자동 축소/재생성 실행 없음.'))
writecsv('SAFE_AREA_REVIEW.csv',safe)
for mid in ['m_snail','m_slime','m_mano']:
    found=[x for x in safe if x['monster_id']==mid]
    message=' 외곽85% 명세 대비 선명한 가로폭 초과: '+', '.join(x['frame']+' '+str(round(x['visible_span_ratio']*100,1))+'%' for x in found)+'. 잘림과 별개로 기술적 여백/배치 보정 후보이며 자동 재생성 사유로 확대하지 않음.'
    D[mid]['changed']+=message;D[mid]['status']='SPEC_MISMATCH'
    for row in review:
        if row['monster_id']==mid and row['role']=='VFX':row['difference']+=message;row['spec_result']='SPEC_MISMATCH'
writecsv('ART_REVIEW.csv',review)
for mid,indices in [('m_snail',[3,5]),('m_slime',[3,4]),('m_mano',[8,9])]:
    r=next(x for x in R if x['monster_id']==mid);size=pic(local(r,r['vfx_files'][0])).width
    b=Image.new('RGBA',(max(950,2*size+52),size+260),BG);d=ImageDraw.Draw(b)
    txt(d,15,10,r['monster_name']+' / 외곽85% 여백 초과 · 원본 1:1',b.width-30,H)
    txt(d,15,54,'노란 상자: 중앙85% 예시. 판정은 중심 위치와 무관한 실제 가로폭 초과에 근거.',b.width-30,SM)
    for j,i in enumerate(indices):
        im=pic(local(r,r['vfx_files'][i]));x=16+j*(size+20);y=125;b.alpha_composite(im,(x,y))
        d.rectangle((x+.075*size,y+.075*size,x+.925*size,y+.925*size),outline='#eaca68',width=1)
        sr=next(a for a in safe if a['monster_id']==mid and a['frame']==f'F{i:02}')
        txt(d,x,94,f'F{i:02} · 선명한 가로폭 {sr["visible_span_px"]}px / {sr["visible_span_ratio"]*100:.1f}%',size,SM)
    txt(d,15,size+160,'새 아트/원화 수정 없이 검사 사본에 경계만 표시. 70% 핵심 형상은 자동 마스크로 분리하지 않았으며 전체 통과를 인증하지 않음.',b.width-30,SM)
    b.convert('RGB').save(P/'evidence'/f'SAFE_AREA_{mid}.png')

# Boundary evidence: exactly three delivered frames with visible clipping, not expanded art.
b=Image.new('RGBA',(1060,650),BG);d=ImageDraw.Draw(b);txt(d,15,10,'마노 / 확정 결함: F05~F07 캔버스 경계의 파형 절단',1030,H)
mr=next(x for x in R if x['monster_id']=='m_mano')
for j,(i,box) in enumerate([(5,(384,288,512,416)),(6,(0,300,128,428)),(7,(0,282,128,410))]):
    im=pic(local(mr,mr['vfx_files'][i]));x=25+350*j
    txt(d,x,65,f'F{i:02} / crop {box}',330,SM);b.alpha_composite(im.crop(box).resize((256,256),Image.Resampling.NEAREST),(x,110))
    d.line((x+(255 if i==5 else 0),110,x+(255 if i==5 else 0),366),fill='#ff7070',width=2)
    txt(d,x,389,('오른쪽' if i==5 else '왼쪽')+' 캔버스 끝 (붉은 선)\n128² crop → 256² / 2×',330,SM)
txt(d,20,480,'F05/F06/F07 경계 alpha 최대 250/250/240. 희박한 먼지 한 점이 아니라 밝은 파형 자체가 끝에서 절단된다. 핵심/외곽 안전영역 요구와 충돌. 원본 파일은 변경하지 않았다.',1020)
b.convert('RGB').save(P/'evidence'/'MANO_CLIPPING_2X.png')

actions=[
dict(id='A00-01',classification='원화 수정 후보',monster_id='m_mano',role='VFX',files='F05;F06;F07',certainty='CONFIRMED',reason='밝은 파형이 캔버스 경계에서 절단. GENERATION_SPEC 외곽85% 안전영역과 충돌.',next_action='이후 수정 승인 시 잘린 파형/배치를 해결하고 12프레임 연결을 다시 확인. 이번에는 수정 안 함. ICON 및 나머지 몬스터 전체 재생성으로 확대하지 않음.',evidence='evidence/MANO_CLIPPING_2X.png'),
dict(id='A00-02',classification='사용자 판단',monster_id='m_snail;m_blue_snail;m_mano;m_slime',role='VFX',files='각 마지막 2~3프레임; 마노 F03→F04',certainty='NEEDS_USER_REVIEW',reason='분절/축소와 알파 면적 감소는 있으나 마지막에 고형 방울/고리가 남음. 슬라임은 덩어리 복원 인상. 마노 지면 고리 위치 변화도 관찰.',next_action='검수용 one-shot/프레임 넘기기로 끝맺음과 고정 중심 인상을 결정. 공백 끝 프레임 강요나 무조건 재생성 금지. 실제 게임 부착점/종료 동작 별도.',evidence='AREA00_REVIEW.html'),
dict(id='A00-03',classification='INPUT 충돌 확인',monster_id='m_snail',role='VFX',files='F03~F05; INPUT ref095; GENERATION_SPEC',certainty='DOCUMENTED_DIFFERENCE',reason='청록 주색/연두 제한 문구와 기존 프로젝트 참고의 강한 연두 광택 사이의 비중 차이.',next_action='당초 원했던 색/재질 비중을 결정. 기존 참고에 가까움과 문자 명세 충족을 같은 것으로 기록하지 않음.',evidence='evidence/m_snail/FULL_COMPARISON.png'),
dict(id='A00-04',classification='사용자 판단',monster_id='all_5',role='VFX;ICON',files='전체 49개 실제 원화',certainty='NEEDS_USER_REVIEW',reason='둥근 유리/젤/진주 광택은 실제 프로젝트 참고와 연결되나, 이것을 전체 게임의 보편적 마감 목표로 채택할지는 승인 사실만으로 결정할 수 없음.',next_action='유체/껍질/진주 표현의 조건부 참고로 채택할지 결정. 저레벨 규모/프레임 수/밀도/곡면광택을 모든 재질과 보스에 강제하지 않음.',evidence='AREA00_REVIEW.html'),
dict(id='A00-05',classification='INPUT 이력 확인',monster_id='all_5',role='DOCUMENT',files='OUTPUT_MANIFEST.md; INPUT global_skill_style_library/summary/STYLE_ATLAS.md',certainty='DOCUMENT_CONFLICT',reason='OUTPUT은 AREA_00_IMAGES_INPUT(2).zip 사용 및 STYLE_ATLAS 미발견이라고 기록. 기준 INPUT에는 STYLE_ATLAS가 존재. 생성 시 동일 바이트 INPUT 사용 여부 불명.',next_action='평가는 지정된 BASELINE INPUT에 고정. 이력 자료 확보 시 별도 확인; 다른 INPUT을 임의 선택하거나 원화를 자동 폐기하지 않음.',evidence='SOURCE_SCOPE.md'),
dict(id='A00-06',classification='유지 가능 / 추가 수정 근거 없음',monster_id='all_5',role='ICON;unaffected_VFX',files='ICON 5개 및 확정 절단 3프레임 이외 원화',certainty='NO_ADDITIONAL_CONFIRMED_ART_EDIT',reason='5스킬의 핵심 소재와 각 ICON 대응, 실제 형태 변화가 확인됨. 전체 재생성을 정당화할 구체적 근거 없음.',next_action='현 상태 보존. 사용자 취향/종료 인상 판단이 남아 있다는 사실과 별개로 확정 수정 범위를 확대하지 않음.',evidence='ART_REVIEW.csv')]
actions[-1]['reason']='5스킬의 핵심 소재와 ICON 대응, 실제 형태 변화 확인. 아래 안전여백 후보와 위 절단 후보를 제외하고 추가 원화 수정/전체 재생성 확정 근거 없음.'
actions[-1]['files']='ICON5개 및 명시된 절단/여백 후보 이외 원화'
actions.append(dict(id='A00-07',classification='기술적 파일/배치 보정 후보',monster_id='m_snail;m_slime;m_mano',role='VFX',files='이슬 F03/F05; 슬라임 F03/F04; 마노 F05~F09',certainty='CONFIRMED_SAFE_MARGIN_SPAN',reason='A>=128의 선명한 가로폭만으로 캔버스85%를 초과하는9프레임. 마노 절단3프레임과 중복되므로 추가 비절단 여백후보는6프레임.',next_action='기준축·크기 의도를 유지하는 여백/배치 보정 방법 확인. 원본 보존 상태로 비교만 수행; 일괄 축소/새 원화 생성하지 않음. 핵심70%는 자동 형상 분할로 인증하지 않음.',evidence='SAFE_AREA_REVIEW.csv; evidence/SAFE_AREA_m_snail.png; evidence/SAFE_AREA_m_slime.png; evidence/SAFE_AREA_m_mano.png'))
writecsv('ACTION_ITEMS.csv',actions)

# Exact SOURCE scope, including document conflict; no real-time resource query is claimed.
iz=zipfile.ZipFile(S[0]['path']);oz=zipfile.ZipFile(S[1]['path'])
(P/'output_documents').mkdir(exist_ok=True)
for n in oz.namelist():
    if n.endswith(('.md','.csv')):
        dst=P/'output_documents'/n.removeprefix('AREA_00_IMAGES_OUTPUT/');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(oz.read(n))
source_rows=[]
for r in R:
    n=r['monster_image'];source_rows.append(dict(area='area_00',monster_id=r['monster_id'],ruid=r['monster_image_ruid'],source_level='INPUT_ONLY',source= S[0]['path']+'::'+n,sha256=hashlib.sha256(iz.read(n)).hexdigest(),limitation='당초 INPUT에 수록된 몬스터 PNG와 명세의 RUID 연결을 대조. 이번에 연결 MSW 리소스를 새 조회하거나 원본 프레임의 해상도를 인증하지 않음. 320×240 제공 썸네일 자체를 1:1로 표시.'))
writecsv('SOURCE_CHECK.csv',source_rows)
checks=[]
for x in S:
    actual=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest();assert actual==x['sha256'];z=zipfile.ZipFile(x['path']);assert z.testzip() is None
    checks.append(dict(kind=x['kind'],path=x['path'],baseline_sha256=x['sha256'],final_sha256=actual,unchanged=True,crc='PASS'))
for r in R:
    for n in r['vfx_files']+[r['icon_file']]:
        src=hashlib.sha256(oz.read(n)).hexdigest();dst=hashlib.sha256(local(r,n).read_bytes()).hexdigest();assert src==dst
        checks.append(dict(kind='DELIVERED_PNG_COPY',path=n,baseline_sha256=src,final_sha256=dst,unchanged=True,crc='ZIP_CRC_PASS'))
writecsv('PRESERVATION_CHECK.csv',checks)

scope='''# 선정·출처·확인 한계

실제 작업 경로는 `D:/maplestory_levup`이다. 사용자에게 주어진 이전 표기 `D:/maplestory/_levup` 대신 실제 BASELINE_INDEX.csv와 승인 ZIP이 존재하는 대응 폴더를 사용했다. 선택값과 해시는 SELECTION.json에 고정했다.

이번 작업은 AREA00 원래 의도/품질 검수다. 이전 골든 샘플·성공·승인 문구는 파일 선택 이외 품질 결론의 근거로 쓰지 않았다. 다른 Area 검수, 생성, 원화 편집, 재패키징, 코드/게임/RUID 수정, Maker 실행은 하지 않았다.

실제 ICON 5장, VFX 44장 전체를 원본 픽셀 크기의 분리 보드로 직접 열어 관찰했다. 183개 INPUT 스타일 preview를 인벤토리 보드에서 선별하고 10개(#035/#067/#084/#092/#094/#095/#100/#101/#178/#180)는 원본 파일 크기로 별도 확인했다. 183개 모두의 정밀 마감·전체 애니메이션을 보았다는 뜻이 아니다.

MONSTER_IMAGE 5장은 INPUT 수록 사본이다. 새 MSW 조회/현재 모델 연결/공식 원본의 원해상도 인증은 이번에 수행하지 않았다. INPUT의 320×240 썸네일을 실제 몬스터의 게임 표시 크기라고 부르지 않았다. 게임 내 배율·부착점·배경·대상 가림·피해/버프 동작·엔진 종료/이동 성공은 미검증이다.

STYLE_INDEX는 RECENT_PRIMARY 0, RECENT_SECONDARY 20, LEGACY_REFERENCE 43, UNKNOWN 120이다. SECONDARY는 6차/HEXA 의미 검색 후보이며 이름/출시일 확인이 낮다. 당초 문서는 이 후보를 우선 참고로 올리지만, 이것이 최신성의 검증 근거가 되지는 않는다. 흰 배경에 합성된 정지 썸네일로 원리소스의 알파 경계·타이밍·전 프레임 동작을 인증할 수도 없다.

OUTPUT_MANIFEST.md는 입력명을 AREA_00_IMAGES_INPUT(2).zip으로 적고 STYLE_ATLAS 미발견이라고 기록한다. 이번 기준 INPUT에는 global_skill_style_library/summary/STYLE_ATLAS.md가 실제로 있다. 생성 당시 INPUT 해시 연결은 이 기록만으로 확정할 수 없다. 이번 평가는 사용자 지정 BASELINE의 당초 요구 대비 관찰이며, 생성 이력을 새로 입증하거나 다른 버전을 추측해 선택하지 않는다.

검수용 HTML은 원본 PNG를 INPUT의 명시된 약 100ms(마노 80ms) 간격으로 보여준다. 보간·엔진 이동·추가 fade 없이 그대로 재생하며 기본은 마지막 프레임을 남긴다. 종료 시 숨기기 옵션은 one-shot 제거 인상을 보기 위한 뷰어 동작이다. 파일의 실제 AnimationClip 타이밍이나 게임 런타임 검증이 아니다. 검수 결론은 직접 연속 정지 프레임 대조에 근거하며 브라우저 재생을 게임 플레이로 보았다고 기록하지 않는다.

PNG_CHECKS / FRAME_MEASUREMENTS는 보조 측정이다. 중심85% 사각형 바깥 알파 픽셀 수를 자동 스타일 점수로 쓰지 않았고, 핵심 형상/파편을 수치만으로 분류하지 않았다. 마지막 프레임을 공백으로 만들라는 요구는 추가하지 않았다. 명시적으로 드러난 마노 파형 절단만 확정 결함으로 분리했다.

중간 안내에서 빨간 달팽이/슬라임을 384×384라고 말한 것은 확인 오류였다. 기준 ZIP 내부 실제 PNG는 모두 256×256이며 명세에 일치한다. 49개 PNG 캔버스/프레임 수/RGBA/실제 투명 영역 확인은 통과했다. 보고서에는 규격 오류를 남기지 않았다.
'''
scope=scope.replace('명시적으로 드러난 마노 파형 절단만 확정 결함으로 분리했다.','마노 파형 절단과 별개로 A>=128의 선명한 가로폭이85%를 초과하는9프레임도 확정 여백 차이로 분리했다. 중심 정렬 해석과 무관한 폭 초과만 사용했으며, 희박한 끝 알파나 한두 픽셀을 모두 원화 수정으로 확대하지 않았다.')
(P/'SOURCE_SCOPE.md').write_text(scope,encoding='utf-8')

summary='''# AREA 00 당초 의도·품질 검수

**조건부 표현 참고로는 사용할 수 있지만, AREA00 전체를 그대로 보편적인 완성 품질 기준으로 쓰기에는 한계가 있다.** 승인 이력과 무관하게 5스킬의 핵심 소재·ICON 연결과 실제 형태 변화는 확인됐다. 그러나 마노 F05~F07에는 명백한 파형 절단이 있고, 종료 인상·재질 해석·당초 참고의 우선순위에는 사용자 판단과 자료 한계가 남는다. 사용자 의도 충족을 대신 승인하지 않는다.

검수 범위: 5몬스터/5스킬, VFX 44프레임+ICON 5개 전부. 5개 MONSTER_IMAGE, 5개 GENERATION_SPEC, 원래 공통 문서와 STYLE_ATLAS를 읽었다. 참고 183개를 선별하고 10개를 1:1로 상세 확인했다. **신규 MSW 원본 조회와 실제 게임 크기/런타임은 미확인**이다. 원화·ZIP·게임 파일은 변경하지 않았다.

## 구현된 부분

| 스킬 | 명세와 대응하는 실제 동작/소재 | 남은 핵심 판단 |
|---|---|---|
| 이슬 미끄럼길 | 낮은 띠→오른쪽 연장/말림→접촉광/분절, 둥근 방울과 ICON 꼬리 | 청록/연두 비중, 마지막 밝은 방울 |
| 푸른 껍질 | 아래 곡선→위로 감싸는 돔/나선→열림/분해 | 단단한 껍질 ICON과 물막 VFX의 재질 차이 |
| 붉은 껍질 돌진 | 적색 원반→오른쪽 추진 잔상→전방 충돌→파편 | 실제 대상 가림/시전자 돌진 결합은 런타임 미확인 |
| 마노의 무지개 파동 | 진주/껍질 결→낮은 무지개 링/상향 빛→분절 | F05~F07 절단, 고정 지면 중심/끝맺음 |
| 끈적한 몸통 | 눌림→점액 가장자리 확장→발현→젤리 수축 | 마지막 온전한 덩어리로 복원되는 종료 인상 |

모든 VFX에서 곡선 분절·돔 형성·충돌 파편·젤리 형태 변화가 실제로 보인다. 단순 균일 확대·축소·투명도 변경만으로 동작 전체를 대신한 사례로 판단하지 않았다. 5 ICON 모두 주요 소재가 64px에서 식별되고 VFX와 색/재질 중심이 연결된다. 마노의 작은 별/방울은 64px에서 합쳐지지만 보스 밀도 차이 자체를 오류로 보지 않는다.

## 확정 결함과 사용자 판단 구분

**확정 원화 수정 후보는 마노 VFX F05~F07의 3프레임**이다. 경계 알파 최대값은 250/250/240이고 밝은 외곽 파형이 잘린다. 원래 85% 외곽 안전영역과 충돌한다. ICON이나 Area 전체 재생성의 근거는 아니다. 수정은 실행하지 않았다. [확대 증거](evidence/MANO_CLIPPING_2X.png)

마노 F03→F04에서 지면 링/중심이 위로 바뀌어 보이는 점은 고정 지면 중심 의도와의 연결을 추가 판단해야 한다. 상향 빛 자체는 명세에 허용되므로 별도 금지 기능이라고 판정하지 않는다.

이슬·푸른 껍질·마노·슬라임은 종료부의 고형 방울/고리 잔존을 사용자 판단으로 남긴다. 실제로 절정보다 알파 면적과 형상이 줄어드므로 ‘fade 없음’이라고 단정하지 않는다. 마지막 공백 프레임을 강요하지 않는다. 슬라임은 끝에서 젤 덩어리로 복원되어 소멸보다 다음 반복의 시작처럼 읽힐 수 있다.

이슬은 청록 주색/연두 제한이라는 문자 요구와 연두가 강한 기존 프로젝트 참고 #095 사이에서 비중 차이가 있다. 결과가 #095에 가깝다는 사실만으로 주색 요구 충족을 자동 인증하지 않는다. 푸른 껍질의 물 같은 막, 빨간 껍질의 불꽃성 잔상, 마노의 장신구 같은 진주, 슬라임의 유리 같은 광택은 구체적인 해석 차이이며 그 자체가 모두 명세 위반은 아니다.

## 실제 참고와 같은 점·다른 점

- #095는 기존 프로젝트의 이슬 VFX다. 둥근 반사 방울, 어두운 청록 외곽, 황백 리본이 AREA00과 직접 연결된다. 공식 최신성이나 독립적인 전체 품질 인증에는 사용할 수 없다.
- #178의 넓은 흰 리본/푸른 반투명 겹, #067의 날카로운 선/어두운 에너지 중심, #100/#101의 유색 층과 밝은 중심은 구체적인 마감 비교점이다. AREA00은 이들보다 곡면·구슬·매끈한 젤 광택을 더 일관되게 사용한다. 물/진주와 수정판/에너지의 정상적인 재질 차이를 구분해야 한다.
- #035의 흐린 안개와 #084의 기계/연기 혼합 자료는 모든 스킬의 정답이 될 수 없다. #092/#094는 프로젝트의 옛 픽셀 ICON이며 새 ICON의 넓은 반사면·연속 명암과 다르지만, 원래 문서도 LEGACY를 보조 참고로 분류한다. 이를 그대로 복제할 의무는 없다.
- OUTPUT 내부에서는 5 ICON의 매끈한 명암/짙은 유색 윤곽이 비교적 통일돼 있다. VFX는 더 부드러운 반투명 가장자리와 밝은 리본을 사용한다. 붉은 껍질의 날카로운 충돌, 마노의 높은 밀도, 슬라임의 젤리 변형은 역할/소재 차이로 설명 가능하다. 한 몬스터 전체가 다른 그림체라고 확정할 증거는 부족하다.

따라서 ‘INPUT의 형태·광택·발현 문법을 상당 부분 구현’은 근거가 있으나 ‘최신 공식 스킬과 같은 마감 수준을 충분히 구현’은 이 자료로 인증할 수 없다. SECONDARY 20개는 출시일/정확한 이름이 확인되지 않았고, 정지 흰 배경 썸네일은 원본 알파와 전체 시간 흐름을 보여주지 않는다.

## 이후 스타일 기준으로 쓸 수 있는 범위

유체/껍질/진주의 소재별 표현 예시, 주요 실루엣과 ICON 대응, 흰 반사면과 유색 중간톤의 층 구분, 형성 후 실제 형태가 바뀌는 흐름은 선택적으로 참고 가능하다. 마노의 절단 프레임과 흔들리는 중심/끝맺음 인상을 모범으로 복제해서는 안 된다. 이 렌더링 방향 자체가 원했던 품질인지는 비교 자료로 사용자가 결정해야 한다.

저레벨 효과 크기, 파편 수, 8/12프레임, 밝은 코어, 곡면 광택을 모든 고레벨·보스·금속·안개·불꽃에 강제하는 전역 규칙으로 확대하지 않는다. 이 작업으로 다른 Area의 원화 변경을 시작하거나 ‘전체 스타일 통일 완료’를 선언하지 않는다.

## 파일 검사와 출처 한계

49 PNG의 요구 캔버스·프레임 수·RGBA와 실제 투명 영역을 확인했다. 빨간 달팽이/슬라임은 256×256으로 정확하다. 기준 INPUT/OUTPUT SHA-256 유지, ZIP CRC 정상, 검수에 복사한 49 납품 PNG 모두 바이트 동일이다. PNG 순번은 연속이며, 재생 시간은 INPUT 약 100ms/마노 80ms를 검수 뷰어에 적용했을 뿐 실제 AnimationClip을 확인한 것은 아니다.

OUTPUT 문서의 ‘INPUT(2), STYLE_ATLAS 미발견’ 기록은 현재 기준 INPUT에 ATLAS가 존재하는 사실과 충돌한다. 이 때문에 생성 당시 동일 INPUT 사용 이력은 확정하지 않았다. 그 사실만으로 결과를 재생성 대상으로 삼지 않는다. 상세 출처·중간 규격 안내 정정은 [SOURCE_SCOPE.md](SOURCE_SCOPE.md)에 기록했다.

## 자료

- [한 화면 검수 뷰어: 5몬스터·요구·참고·전체 프레임·ICON·재생](AREA00_REVIEW.html)
- [역할별 실제 판단 10행](ART_REVIEW.csv), [조치/판단 묶음](ACTION_ITEMS.csv)
- [원본 선정](SELECTION.json), [바이트 보존/CRC](PRESERVATION_CHECK.csv)
- [참고별 분류와 사용 한계](REFERENCE_QUALIFICATION.csv), [전체 참고 인덱스](REFERENCE_INVENTORY.csv)
- [몬스터별 비교 자료 위치](EVIDENCE_INDEX.csv), [프레임 보조 측정](FRAME_MEASUREMENTS.csv)
'''
summary=summary.replace('## 실제 참고와 같은 점·다른 점','''**별도의 기술적 여백 차이:** 이슬 F03/F05(가로폭86.5%/87.5%), 슬라임 F03/F04(90.6%/85.9%), 마노 F05~F09(94.7%/100%/97.1%/89.5%/86.1%)는 외곽85% 제한을 넘는다. 선명한 A>=128 영역만 사용한 보수적 확인이고, 상자를 어디에 놓더라도 가로폭 자체가 크다. 총9프레임 중 마노 절단3프레임은 중복이며, **추가 비절단 여백/배치 보정 후보는6프레임**이다. 새 그림을 반드시 그려야 한다는 뜻은 아니다. 핵심70%는 의미별 형상 마스크를 자동 추정해 통과 처리하지 않았다. [수치/파일](SAFE_AREA_REVIEW.csv), [이슬 비교](evidence/SAFE_AREA_m_snail.png), [슬라임 비교](evidence/SAFE_AREA_m_slime.png), [마노 비절단부 비교](evidence/SAFE_AREA_m_mano.png)

역할별 명세 집계는 SPEC_MISMATCH 3(VFX: 이슬/마노/슬라임), NEEDS_USER_REVIEW 1(푸른 껍질 VFX), NO_OBVIOUS_ISSUE 6(붉은 껍질 VFX+ICON5)이다. 이 집계는 사용자 품질 승인이나 스타일 통일 인증이 아니다.

## 실제 참고와 같은 점·다른 점''')
(P/'REVIEW_SUMMARY.md').write_text(summary,encoding='utf-8')

# Review interface: existing images only; fixed canvas; manual stepping and optional one-shot.
parts=['''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>AREA00 당초 의도·품질 검수</title><style>
body{background:#171c24;color:#edf0f6;font:16px/1.7 "Malgun Gothic",sans-serif;margin:0}main{max-width:1180px;margin:auto;padding:28px}h1{font-size:28px}h2{font-size:24px;border-top:1px solid #526072;padding-top:28px}a{color:#9bdbff}nav{display:flex;gap:18px;flex-wrap:wrap;position:sticky;top:0;background:#171c24;padding:12px;z-index:2}.note{background:#2a3546;padding:16px;border-left:4px solid #ffc97c}.row{display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start}figure{margin:8px 0;max-width:100%}figcaption{font-size:14px;color:#c4d0df}img{vertical-align:top}.page{display:block;max-width:100%;height:auto;margin:18px 0}.scroll{overflow:auto;background:#202630}.stage{position:relative;overflow:hidden;background:#202630;flex-shrink:0}.stage img{position:absolute;left:0;top:0;max-width:none}.controls{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}button,select{font:inherit;padding:6px 12px;cursor:pointer}table{border-collapse:collapse}td,th{border:1px solid #4d5b6f;padding:8px}details{margin:15px 0}code{overflow-wrap:anywhere}section{scroll-margin-top:75px}.pill{color:#ffcf86} .native{max-width:none} .small{font-size:14px;color:#bdc9d8}</style><main>
<h1>AREA 00은 원했던 디자인·마감을 구현했는가?</h1><p class="note">조건부 표현 참고로 사용 가능. 전체를 무조건적인 완성 품질 기준으로 확정하지 않음. 마노 F05~F07 파형 절단은 확정 결함이며, 재질 해석·끝맺음·자료 최신성의 한계가 남습니다. 사용자 승인/게임 동작 성공을 뜻하지 않습니다.</p>
<nav>''']
parts += [f'<a href="#{r["monster_id"]}">{e(r["monster_name"])}</a>' for r in R]
parts.append('</nav><p><a href="REVIEW_SUMMARY.md">전체 보고서</a> · <a href="ACTION_ITEMS.csv">문제/결정 목록</a> · <a href="SOURCE_SCOPE.md">출처와 한계</a></p><p class="small">원본 픽셀 1:1은 파일의 픽셀 크기입니다. 실제 게임 크기가 아닙니다. 아래 프레임 뷰어는 보간·이동·추가 fade 없이 기존 PNG만 표시합니다. INPUT의 약 100ms(마노 80ms) 간격은 런타임 타이밍 인증이 아닙니다.</p>')
for r in R:
    v=r['review'];mid=r['monster_id'];size=pic(local(r,r['vfx_files'][0])).width
    parts.append(f'<section id="{mid}"><h2>{e(r["monster_name"])} · {e(r["skill_name"])}</h2><p class="pill">{e(v["status"])} · 사용자 최종 승인 없음</p><p><code>{e(mid)} / {e(r["skill_id"])}</code></p>')
    for title,key in [('당초 요구','req'),('구현된 부분','implemented'),('빠지거나 달라진 점 / 확인 한계','changed'),('실제 참고와의 마감 비교','finish'),('명세와 별개인 사용자 판단','taste')]:parts.append(f'<h3>{title}</h3><p>{e(v[key])}</p>')
    parts.append(f'<a href="{r["pages"][0]}"><img class="page" src="{r["pages"][0]}" alt="원본 몬스터·요구·참고·ICON 비교"></a><p class="small">보드가 화면 폭에 맞게 줄어들면 클릭하여 원본 픽셀 크기로 확인하세요. 아래 뷰어는 1:1 표시가 기본입니다.</p>')
    parts.append(f'''<div class="controls"><button data-play="{mid}">한 번 재생</button><button data-prev="{mid}">이전 프레임</button><button data-next="{mid}">다음 프레임</button><button data-reset="{mid}">F00</button><label><input type="checkbox" id="hide-{mid}"> 끝에서 숨김 (검수용)</label><select data-bg="{mid}"><option value="#202630">어두운 배경</option><option value="#ffffff">흰 배경</option><option value="#777777">회색 배경</option></select><select data-scale="{mid}"><option value="1">원본 1:1</option><option value="2">2배 · 최근접 픽셀</option></select><span id="label-{mid}">F00</span></div><div class="scroll"><div class="stage" id="stage-{mid}" style="width:{size}px;height:{size}px"><img id="anim-{mid}" src="{r['native_files'][0]}" width="{size}" height="{size}" alt="실제 VFX 프레임"></div></div>''')
    parts.append('<h3>실제 VFX 전체 프레임 · 순서대로</h3><div class="row">')
    for i,n in enumerate(r['native_files']):parts.append(f'<figure><figcaption>F{i:02} · {size}×{size}</figcaption><a href="{n}"><img class="native" src="{n}" width="{size}" height="{size}" alt="F{i:02}"></a></figure>')
    parts.append('</div>')
    parts.append(f'<h3>2배 상세 비교</h3><a href="{r["pages"][-1]}"><img class="page" src="{r["pages"][-1]}" alt="참고·VFX·ICON 동일 배율 확대"></a><p><a href="evidence/{mid}/FULL_COMPARISON.png">몬스터별 전체 비교 PNG</a> · <a href="input_documents/{e(r["folder"])}/GENERATION_SPEC.md">원래 명세 전문</a></p></section>')
parts.append('<h2>확정 결함 확대</h2><img class="page" src="evidence/MANO_CLIPPING_2X.png" alt="마노 세 프레임의 경계 절단"><h3>추가 안전여백 차이: 절단3개와 중복되는 총9프레임</h3><p>추가 비절단 여백/배치 보정 후보는6프레임. 원화 생성 필요와 구분합니다.</p>')
for mid in ['m_snail','m_slime','m_mano']:parts.append(f'<img class="page" src="evidence/SAFE_AREA_{mid}.png" alt="{mid} 안전여백 비교">')
parts.append('<p>원본 ZIP/PNG/게임 파일 변경 없음. 다른 Area의 수정·생성은 시작하지 않았습니다.</p></main>')
config={r['monster_id']:dict(files=r['native_files'],dt=r['dt_ms'],size=pic(local(r,r['vfx_files'][0])).width) for r in R}
js='''const config=CONFIG; const state={};
for(const [id,c] of Object.entries(config)){state[id]={i:0,timer:null};c.files.forEach(src=>{const im=new Image();im.src=src;});}
function stop(id){clearTimeout(state[id].timer);state[id].timer=null;}
function show(id,i){const s=state[id],c=config[id];s.i=(i+c.files.length)%c.files.length;const el=document.getElementById('anim-'+id);el.src=c.files[s.i];el.style.visibility='visible';document.getElementById('label-'+id).textContent='F'+String(s.i).padStart(2,'0')+' / '+c.dt+'ms';}
async function play(id){stop(id);const c=config[id];await Promise.all(c.files.map(src=>new Promise(resolve=>{const im=new Image();im.onload=resolve;im.onerror=resolve;im.src=src;})));show(id,0);function tick(){if(state[id].i<c.files.length-1){show(id,state[id].i+1);state[id].timer=setTimeout(tick,c.dt);}else{if(document.getElementById('hide-'+id).checked)document.getElementById('anim-'+id).style.visibility='hidden';state[id].timer=null;}}state[id].timer=setTimeout(tick,c.dt);}
document.querySelectorAll('[data-play]').forEach(b=>b.onclick=()=>play(b.dataset.play));
for(const k of ['prev','next','reset'])document.querySelectorAll('[data-'+k+']').forEach(b=>b.onclick=()=>{const id=b.dataset[k];stop(id);show(id,k==='reset'?0:state[id].i+(k==='next'?1:-1));});
document.querySelectorAll('[data-bg]').forEach(s=>s.onchange=()=>document.getElementById('stage-'+s.dataset.bg).style.background=s.value);
document.querySelectorAll('[data-scale]').forEach(s=>s.onchange=()=>{const id=s.dataset.scale,c=config[id],n=Number(s.value),stage=document.getElementById('stage-'+id),im=document.getElementById('anim-'+id);stage.style.width=c.size*n+'px';stage.style.height=c.size*n+'px';im.style.width=c.size*n+'px';im.style.height=c.size*n+'px';im.style.imageRendering=n===2?'pixelated':'auto';});
'''.replace('CONFIG',json.dumps(config,ensure_ascii=False))
(P/'viewer.js').write_text(js,encoding='utf-8');parts.append('<script src="viewer.js"></script></html>')
(P/'AREA00_REVIEW.html').write_text('\n'.join(parts),encoding='utf-8')
(P/'REVIEW_DATA.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote AREA00 review: 5 monsters, 44 VFX, 5 ICON, 10 role rows, 7 action groups. Preserved 2 ZIPs + 49 PNG bytes.')
