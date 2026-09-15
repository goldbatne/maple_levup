from pathlib import Path
import json
root=Path(__file__).parent
packs=[p for f in sorted(root.glob('page_*.json')) for p in json.loads(f.read_text())['items']]
choices={
 'water':('162141004',['hit/0'],'물방울의 두께·명암과 물 타격의 분해'),
 'barrier':('162121022',['prepare','keydown','keydownend'],'보호막의 준비·유지·해체와 층이 겹치는 구조'),
 'mist':('2141004',['tile','special','hit/0'],'입자 구름의 밀도 변화와 가장자리 분산; 독 색상은 복제하지 않음'),
 'garden':('13141500',['customEffect/start/0','customEffect/end/0','hit/0'],'꽃잎·바람의 면 분리와 정돈된 작은 입자; 소환체는 복제하지 않음'),
 'curse':('152000010',['mob/1','hit/0'],'작은 저주 표식의 읽힘과 국소 타격광'),
 'star':('65141001',['effect','effect1'],'마력 덩어리의 코어·중간톤·꼬리 표현; 공식 모티브는 복제하지 않음'),
 'ice':('2241003',['effect','hit/0'],'얼음 결정의 면·밝은 코어와 파편 해체'),
 'earth':('164141031',['effect','effect0','hit/0'],'지면 솟구침·암석 면 분리·흙 파편의 무게감'),
 'machine':('36141000',['effect','special','hit/0'],'정밀 에너지 광선과 기계적 명암 경계; 총기 모양은 복제하지 않음'),
 'time':('100001261',['effect','tile/begin/0','tile/0/0','tile/end/0'],'공간장의 시작·유지·종료와 겹친 광륜'),
 'psychic':('142140003',['effect','effect2','hit/0'],'압력·왜곡과 각진 충격 면의 대비'),
 'metal':('51141002',['effect_ple/pre','effect_ple/loop','effect_ple/end'],'단단한 방호광의 명암과 전개; 문장·방패 디자인은 복제하지 않음'),
 'fire':('12141000',['effect','hit/0'],'불꽃 내부 코어·중간톤 혀·외곽 불티'),
 'sand':('154141500',['prepare','keydown','keydownend','hit/0'],'먼지의 다층 밀도·폭풍 궤적·시간 전개'),
 'needle':('63121006',['effect/0','effect/1','effect/2'],'가늘고 날카로운 타격의 층과 잔상; 원본 공격 동작은 복제하지 않음'),
 'wind':('162141005',['effect','effect0','hit/0'],'바람의 면과 투명 경계·흐름; 정령 본체는 복제하지 않음'),
 'lightning':('2241000',['effect','hit/0'],'번개의 코어와 색 외곽·분지의 정돈')}
details={x['id']:x for f in (root/'details').glob('*.json') for x in json.loads(f.read_text()).get('items',[])}
selected=[]
for key,(sid,roles,purpose) in choices.items():
 p=next(p for p in packs if p['id'].endswith('/'+sid))
 elements=[e for e in p['payload']['elements'] if e['rel_path'] in roles+['icon'] and e['resource_type'] in ['sprite','animationclip']]
 assert any(e['rel_path']!='icon' for e in elements),key
 selected.append(dict(key=key,pack_id=p['id'],names=p.get('names'),purpose=purpose,currentness='UNVERIFIED; VI label is not proof of latest live revision',elements=[dict(e,detail=details[e['ruid']]) for e in elements]))
(root/'selected.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8')
print('Selected',len(selected),'groups',sum(len(x['elements']) for x in selected),'images')
