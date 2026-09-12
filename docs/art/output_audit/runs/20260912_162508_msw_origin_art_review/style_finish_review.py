from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,csv,zipfile,io,hashlib,textwrap,collections
P=Path(__file__).parent
R=json.loads((P/'STYLE_SELECTED_RECORDS.json').read_text(encoding='utf-8'))
B=json.loads((P/'STYLE_AREA00_FILES.json').read_text(encoding='utf-8'))
C=json.loads((P/'CONTRACT_SNAPSHOTS.json').read_text(encoding='utf-8'))
CM={(x['area_id'],x['monster_id'],x['role']):x for x in C}
RM={(x['area_id'],x['monster_id']):x for x in R}
F=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
FB=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',22)
BG=(32,38,48,255)
def png(z,n):
 with zipfile.ZipFile(z) as f:return Image.open(io.BytesIO(f.read(n))).convert('RGBA')
def get(a,m,role,i=0):
 r=RM[(a,m)];return png(r['output_zip'],r['role_files'][role][i])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wc(n,rows):
 with (P/n).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def base(role,size):
 key=next(k for k in B['files'] if ('m_blue_snail_' if size==256 else 'm_mano_' if size==512 else 'm_slime_') in k)
 rr='ICON' if role=='ICON' else 'CAST_VFX'
 i=0 if rr=='ICON' else (6 if size==512 else 4)
 return key,B['files'][key][rr][i]
issues={}
def add(a,m,roles,status,reason,finish):
 for role in roles:issues[(a,m,role)]={'status':status,'reason':reason,'finish':finish}
O='STYLE_OUTLIER';U='NEEDS_USER_REVIEW'
for r in R:
 a,m=r['area_id'],r['monster_id']
 if a=='area_05':add(a,m,['ICON'],O,'256px 원본에서 곡선 외곽과 흰 하이라이트가 굵은 계단형 픽셀 군집으로 끊긴다. AREA00 ICON의 연속적인 곡선·색면 경계와 다르며, 같은 Area의 리본/별가시/집게 CAST는 부드러운 회화적 마감이다.','실루엣·대표색을 유지하고 외곽 계단, 하이라이트의 사각 단위, 명암 경계를 AREA00에 맞춰 정돈')
 if a in ['area_14','area_18']:
  for role in r['role_files']:
   add(a,m,[role],O,'외곽·광륜·명암 경계가 반복되는 픽셀 계단과 덩어리 색면으로 구성된다. AREA00의 연속 곡선/얇은 광선/부분적인 부드러운 반투명 마감과 차이가 있다. 같은 Area 내부에는 이어지지만 액체·금속·빛 등 여러 소재에 공통인 제작 마감 차이다.','소재·형상·팔레트·역할·프레임 수를 보존하고 외곽 및 명암 연결, 광선 끝, 입자 가장자리의 마감만 통일 후보')
 if a=='area_02' and m!='m_fire_boar':add(a,m,['ICON'],U,'금속·나무·뼈·돌을 둘러싼 두꺼운 거의 검은 외곽과 거친 면 질감이 AREA00 및 AREA20의 더 가는 윤곽보다 강조된다. 소재의 거칠기는 허용되므로 곧바로 오류로 확정하지 않는다.','소재의 결은 유지. ICON 외곽 굵기와 검은 테두리 강조를 허용할지 사용자 판단')
add('area_05','m_blue_pig',['REFERENCE_VFX'],O,'F00–F05 리본과 고리의 가장자리가 계단형 픽셀 선이고 명암 띠가 굵게 끊긴다. 같은 소재인 리본돼지 CAST의 곡선 그라데이션과 차이가 있다.','푸른 매듭·조임 고리와 짧은 호흡을 유지; 리본 음영과 광륜 가장자리 마감 정돈')
add('area_05','m_jellyfish',['REFERENCE_VFX'],O,'F00–F05 젤리의 곡선, 하이라이트, 십자 입자가 사각 픽셀 군집이다. AREA00 슬라임의 유체 윤곽·곡면 하이라이트와 차이가 있어 서리라는 소재 차이만으로 설명하기 어렵다.','젤리·서리 튐과 호흡을 유지; 액체 윤곽·반사광·입자 마감 정돈')
add('area_11','m_ratz',['REFERENCE_VFX'],O,'F00–F05 톱니에 굵은 계단형 검은 윤곽과 단순한 고리 음영이 반복된다. 같은 스킬 ICON의 부드러운 금속 반사 및 AREA12 타이머의 세밀한 금속 모서리와 다르다.','톱니 맞물림/민첩 잔상은 유지; 금속 경사면·윤곽·반사광 정돈')
add('area_11','m_bloctopus',['REFERENCE_VFX'],O,'F00–F05 블록의 윤곽과 명암이 굵은 픽셀 띠로 끊긴다. 사각 형상 자체가 문제가 아니라 같은 ICON의 매끄러운 반투명 면과 외곽 마감이 다른 점이다.','사각 블록·위장막·흐림 격자 유지; 면 그라데이션과 투명 가장자리 마감 정돈')
add('area_11','m_king_bloctopus',['PROJECTILE'],O,'F00–F03 왕관과 분홍 코어/포구의 두꺼운 계단 윤곽·픽셀 명암이 CAST의 부드러운 블록 면과 다르다. 축소 본체처럼 읽히는 조합은 별도의 기존 SPEC_MISMATCH다.','왕관 블록 핵·각진 조각 유지. 기존 명세 위반 해결 후보와 함께 CAST/ICON의 면·외곽 마감에 맞춤; 투명도 보류 별도')
add('area_12','m_toy_trojan',['ICON'],O,'목마 머리의 외곽·갈기·명암 띠가 굵은 픽셀 계단으로 읽혀 CAST의 매끈한 목재/태엽 및 AREA00 ICON의 곡선 처리와 다르다. 눈 있는 머리는 ICON에서 허용되므로 본체 금지 위반으로 판단하지 않는다.','허용된 목마 머리·태엽 모티브 유지; ICON 외곽·목재 명암 마감만 후보. CAST 유지')
add('area_12','m_brown_teddy',['REFERENCE_VFX'],O,'F00–F05 쿠션 외곽과 솜 덩어리에 계단형 윤곽 및 굵은 픽셀 명암 띠가 보인다. ICON의 미세한 섬유/부드러운 솜 층과 차이가 있다.','쿠션·솜·비전투 호흡을 유지하고 솜/패딩 경계와 명암 마감 정돈')
add('area_12','m_master_robo',['REFERENCE_VFX'],O,'F00–F05 톱니/장갑의 검은 계단형 선과 평평한 회색 띠가 반복된다. 같은 ICON의 경사진 금속 반사면과 다른 마감이다.','톱니 장갑 유지; 외곽·금속 경사면과 발광선 정돈. ICON 수정 대상으로 확대하지 않음')
add('area_13','m_scarf_plead',['REFERENCE_VFX'],O,'F00–F05 목도리에 계단형 외곽과 줄무늬처럼 분리된 명암이 보인다. 같은 ICON 및 리본돼지 CAST의 직물 곡면/부드러운 광선과 다르다.','목도리·속도 잔상·호흡 유지; 직물 주름 음영 및 끝단 마감 정돈')
add('area_08','m_star_pixie',['PROJECTILE'],U,'F00–F03 둥근 별의 평평한 황색 내부와 두꺼운 테두리가 CAST/ICON의 입체 별핵보다 배지처럼 읽힌다. 발광 핵의 단순화로 볼 여지가 있어 이탈 확정은 보류한다.','별핵/짧은 꼬리와 방향 중립 유지. 테두리 및 내부 입체감의 허용 범위 사용자 판단')
add('area_08','m_luster_pixie',['REFERENCE_VFX'],U,'F00–F05 평평한 원판·삼각 광선과 날개 면이 ICON의 입체 태양핵/깃털보다 기호에 가깝다. 정지 모티브의 짧은 호흡이라는 역할상 단순화는 허용되므로 예외 여부 판단이 필요하다.','태양핵·날개형 잔상과 비전투 호흡 유지; 원판/날개 명암의 단순화 허용 여부 판단')
add('area_15','m_peach_monkey',['PROJECTILE'],U,'F00–F03 복숭아의 어두운 계단형 외곽과 분리된 명암이 같은 ICON/CAST보다 강조된다. 작은 비행체의 가독성 목적일 가능성이 있어 확정 이탈과 분리한다.','복숭아·직선 잔상·로컬 중심 유지; 외곽과 음영 단순화 허용 여부 판단')
def evidence(k,v):
 a,m,role=k;r=RM[(a,m)];files=r['role_files'][role];i=0 if role=='ICON' else len(files)//2
 target=png(r['output_zip'],files[i]);bk,bn=base(role,target.width);bi=png(B['zip'],bn)
 cr=next(x for x in r['role_files'] if (x!='ICON' if role=='ICON' else x=='ICON'))
 cf=r['role_files'][cr];ci=0 if cr=='ICON' else len(cf)//2;comp=png(r['output_zip'],cf[ci])
 im=Image.new('RGBA',(1600,1250),BG);d=ImageDraw.Draw(im)
 d.text((20,15),f'{a} / {m} / {r["skill_name"]} / {role}',font=FB,fill='white')
 d.text((20,49),v['status']+' | 위: 원본 1:1 / 아래: 동일 128px 중앙 영역 2배 NEAREST 확대',font=F,fill='#ffce7d')
 for col,(pic,label) in enumerate([(bi,'AREA00 승인 '+bk),(target,role+f' F{i:02d}' if role!='ICON' else '실제 ICON'),(comp,'동일 스킬 '+cr)]):
  x=20+col*525;d.text((x,85),label,font=F,fill='white');im.alpha_composite(pic,(x+(510-pic.width)//2,118+(512-pic.height)//2))
  box=(pic.width//2-64,pic.height//2-64,pic.width//2+64,pic.height//2+64)
  im.alpha_composite(pic.crop(box).resize((256,256),Image.Resampling.NEAREST),(x+125,645))
 yy=922
 for line in textwrap.wrap(v['reason'],width=86):d.text((20,yy),line,font=F,fill='white');yy+=28
 motif=next((l[2:] for l in r['spec'].splitlines() if l.startswith('- 핵심 소재:')),'')
 for line in textwrap.wrap(motif,width=88):d.text((20,yy+10),line,font=F,fill='#b8d8ec');yy+=27
 d.text((20,1205),'색/해상도/명암 보정 없음. 전체 프레임·실제 파일 경로·명세는 CSV 및 NATIVE 보드 참조.',font=F,fill='#bac5d4')
 dest=P/'STYLE_OUTLIERS'/f'{a}_{m}_{role}_COMPARE.png';im.convert('RGB').save(dest)
 return str(dest),bn,files[i],cf[ci]
if __name__=='__main__':
 rows=[]
 for k,v in issues.items():
  path,bn,fn,comp=evidence(k,v);rows.append(dict(zip(['area_id','monster_id','role'],k))|v|{'board':path,'baseline_file':bn,'detail_frame':fn,'companion_file':comp})
 wc('STYLE_OUTLIERS/INDEX.csv',rows)
 (P/'STYLE_VISUAL_DECISIONS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 print(collections.Counter(x['status'] for x in rows))
