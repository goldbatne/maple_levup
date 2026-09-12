from review_audit import *
from collections import Counter
from datetime import datetime,timezone
RS=json.loads((RUN/'records.json').read_text('utf8'))
OLDROWS={r['monster_id']:r for r in readcsv(OLD/'CONTENT_STYLE_REVIEW.csv')}
def line(r,key):return next((l[len('- '+key+':'):].strip() for l in r['spec'].splitlines() if l.startswith('- '+key+':')),'')
def main():
    sources=[];reviews=[];contracts=[]
    downloads={r['ruid']:r for r in json.loads((RUN/'download_log.json').read_text('utf8'))}
    meta={r['id']:r for r in json.loads((RUN/'resource_metadata.json').read_text('utf8'))}
    mon={r['id']:r for r in readcsv(ROOT/'RootDesk/MyDesk/GameData/MonsterTable.csv')}
    skills={r['id']:r for r in readcsv(ROOT/'Mislocated/MyDesk/GameData/SkillTable.csv')}
    selections={r['area_id']:r for r in readcsv(RUN/'AREA_SELECTION.csv')}
    batches={}
    for p in sorted(RUN.glob('resource_batch_*.json')):
        b=json.loads(p.read_text('utf8'))
        for rid in b['ids']:batches[rid]={'file':str(p),'query_time':b['queried_at'],'endpoint':b['endpoint']}
    for r in RS:
        mid=r['monster_id'];rid=r['monster_image_ruid'];iz=zipfile.ZipFile(r['input_zip']);sel=selections[r['area_id']];d=downloads[rid];ma=mon[mid]
        src={'area_id':r['area_id'],'monster_id':mid,'monster_name':r['monster_name'],'project_model_id':ma['model_id'],'project_model_path':r['model_path'],'model_sha256':r['model_sha256'],'sprite_animation_ruid':rid,'action_sheet':json.dumps(r['model_action_sheet'],ensure_ascii=False),'model_child_count':r['model_children'],'project_monster_name_match':r['project_name_match'],'project_skill_link_match':r['project_skill_match'],'source_level':'MSW_ORIGINAL_CONFIRMED','resource_type':meta[rid]['type'],'resource_names':json.dumps(r['source_names'],ensure_ascii=False),'resource_query_endpoint':batches[rid]['endpoint'],'resource_query_at':batches[rid]['query_time'],'resource_query_evidence':batches[rid]['file'],'source_image_url':d['url'],'source_copy_path':d['file'],'source_copy_sha256':d['sha256'],'source_download_at':d['queried_at'],'api_frame_count':len(r['source_api_frames']),'gif_frame_count':r['source_gif_frames'],'api_frame_ruids':'|'.join(r['source_api_frames']),'resource_version':'API does not expose immutable revision; query time + returned metadata + image SHA256 snapshot','input_zip':r['input_zip'],'input_zip_sha256':sel['input_sha256'],'input_image':r['input_image'],'input_image_sha256':hashlib.sha256(iz.read(r['input_image'])).hexdigest(),'identity_finding':'공식 exact-RUID clip 영상과 INPUT의 실루엣·몸색·얼굴/장비 구성을 직접 대조. 동일 개체로 읽힘. 흰 배경/투명화·동작 프레임 차이는 정체성 불일치로 보지 않음.','visual_evidence':str(RUN/'boards'/f'{r["area_id"]}_source_and_all_frames.png'),'visual_frame_scope':'GIF 전체 프레임 접촉시트; 9f 이상은 source_detail_01..05에서 첫/중간/끝 확대 추가','unverified_reason':'없음(정체성 확인 범위). attack/hit/die의 모든 별도 clip 및 엔진 렌더 검증은 범위 밖'}
        sources.append(src)
        scope={x['effect_role']:x for x in zcsv(iz,r['input_prefix']+'FULL_ART_SCOPE.csv') if x['monster_id']==mid}
        req={x['effect_role']:x for x in zcsv(iz,r['input_prefix']+'OUTPUT_REQUIREMENTS.csv') if x['monster_id']==mid}
        binding={x['effect_role']:x for x in zcsv(iz,r['input_prefix']+'ASSET_BINDING_PLAN.csv') if x['monster_id']==mid}
        runtime_path=r['input_prefix']+r['folder']+'/RUNTIME_ROLE_MAP.md';runtime=iz.read(runtime_path).decode('utf-8-sig')
        assert f"required_roles: `{r['required_roles']}`" in runtime
        assert set(r['role_files'])=={k for k,v in req.items() if v['required']=='true'}
        for role,files in r['role_files'].items():
            sc=scope[role];rq=req[role];bi=binding[role]
            assert len(files)==int(rq['frame_count'])
            assert sc['production_decision']==rq['production_decision']==bi['decision']
            contract={'area_id':r['area_id'],'monster_id':mid,'skill_id':r['skill_id'],'role':role,'full_art_scope':sc,'output_requirements':rq,'asset_binding_plan':bi,'runtime_role_map_path':runtime_path,'runtime_role_map':runtime,'generation_spec_path':r['input_prefix']+r['folder']+'/GENERATION_SPEC.md','generation_spec':r['spec'],'current_skill_candidate':skills[r['skill_id']]}
            contracts.append(contract)
            observation=OLDROWS[mid]['observed_visual_sequence']
            # Prior descriptions of these two monsters are contradicted by the actual frames.
            if mid=='m_king_bloctopus':
                observation={'ICON':'왕관을 얹은 보라 블록과 각진 뒤쪽 궤적. 눈이 없는 추상 블록/포구 모티브로 UI 식별이 됨.','CAST_VFX':'F00 파편 집결 → F01~F03 눈·포구 없는 왕관/입방체 조립 → F04 섬광 → F05 오른쪽 발사 → F06~F07 잔광. 원본의 얼굴/촉수 본체는 확인되지 않음.','PROJECTILE':'F00~F03에 원본과 같은 분홍 사각 몸통, 검은 눈, 원형 포구, 왕관 조합이 반복됨. 촉수가 없어도 얼굴/몸통을 포함한 축소 개체로 읽힘. 각진 조각과 맥동만 변하고 중심 위치는 유지됨.'}[role]
            if mid=='m_toy_trojan':
                observation='ICON에는 눈 달린 목마 머리, 태엽, 바퀴와 짧은 속도선이 있음. 명시적 ICON 모티브.' if role=='ICON' else 'F00~F03의 금색 이중 고리는 태엽 구멍, 갈색 동심원은 바퀴/축이다. 곡선 나무편과 충돌광 뒤 F04~F07 속도선·파편이 소멸한다. 384px 원본 확대에서 눈·귀·주둥이를 갖춘 머리나 상체를 확인하지 못함. 전신 돌진의 반복이 아닌 도착점 충돌 연출.'
            if mid=='m_mutant_stone_mask':observation='갈색 돌판/가면 조각이 원형 보호판으로 맞물리고 반사광 뒤 분리된다. 섬유 소재를 관찰했다고 해석하지 않음.'
            status='SPEC_MISMATCH' if mid=='m_king_bloctopus' and role=='PROJECTILE' else 'NO_OBVIOUS_ISSUE'
            reasoning='실제 프레임에 눈·포구·분홍 몸통이 결합되어 VFX의 몸·얼굴 금지와 충돌. 왕관·각진 블록·에너지 조각 자체는 허용. PROJECTILE 4장만 수정 후보이며 CAST/ICON은 제외.' if status=='SPEC_MISMATCH' else '아래 실제 관찰과 역할 계약을 대조한 범위에서 구체적 충돌 없음. 몬스터의 색/재질/장비를 스킬 모티브로 번역한 것으로 읽힘.'
            if mid=='m_toy_trojan' and role=='CAST_VFX':reasoning='이전 보고의 눈 달린 머리/상체 주장을 실제 프레임에서 재현하지 못했다. 허용된 바퀴·태엽·나무 파편이므로 현행 문구 유지 가능하며 예외 승인 불필요.'
            if mid=='m_king_bloctopus' and role=='CAST_VFX':reasoning='이전 보고가 PROJECTILE의 얼굴/포구를 CAST에까지 일반화한 부분을 철회한다. CAST는 눈 없는 왕관 블록을 원점 부근에서 조립·발사하며 현재 CAST 계약과 맞는다.'
            engine=sc.get('direction_and_engine_motion','')
            rolebasis={'ICON':'256px 원본 및 64px 축소에서 대표 모티브와 보조 효과 확인. VFX와 같은 색/소재 계열로 읽힘.','CAST_VFX':'모든 납품 프레임의 형성·발현·해체·소멸과 역할별 방향을 접촉시트에서 확인. 도착점/발사 준비/판정 범위의 구분 적용. 엔진의 실제 위치·판정 성공은 검증하지 않음.','REFERENCE_VFX':'6프레임 비전투 참고 표현으로 평가. 패시브에 실제 CAST나 지속 버프 호출이 있다고 추정하지 않음.','PROJECTILE':'4프레임의 중심 비행체와 국소 맥동/입자를 확인. 짧은 꼬리 허용 여부는 개별 명세에 따름. 엔진 이동거리·회전을 전체 이동 궤적으로 중복하는 명백한 표현은 보이지 않음.'}[role]
            evidence=src['visual_evidence']
            if mid in ['m_king_bloctopus','m_toy_trojan']:evidence+='|'+str(RUN/'evidence'/f'{r["area_id"]}_{mid}_comparison.png')
            reviews.append({'area_id':r['area_id'],'monster_id':mid,'monster_name':r['monster_name'],'skill_id':r['skill_id'],'skill_name':r['skill_name'],'skill_type':r['skill_type'],'role':role,'art_judgment':status,'configuration_fit':status,'style_judgment':'NO_OBVIOUS_ISSUE','output_zip':r['output_zip'],'output_zip_sha256':sel['output_sha256'],'actual_output_files':'|'.join(files),'actual_output_file_sha256':json.dumps({n:r['file_hashes'][n] for n in files},ensure_ascii=False),'input_zip':r['input_zip'],'input_version':'V2.4','input_zip_sha256':sel['input_sha256'],'input_spec_path':contract['generation_spec_path'],'input_runtime_role_map':runtime_path,'input_core_material':line(r,'핵심 소재'),'input_role_contract':line(r,'런타임 역할'),'input_icon_motif':line(r,'아이콘 핵심 모티브'),'input_body_prohibition':line(r,'몬스터 본체 금지 범위'),'input_timing_flow':line(r,'시간 흐름'),'direction_and_engine_motion':engine,'confirmed_effect':r['actual_effect'],'declared_runtime_effect':r.get('runtime_effect',''),'declared_runtime_motion':r.get('runtime_motion',''),'role_runtime_use':rq['runtime_use'],'production_decision':rq['production_decision'],'required_frame_count':rq['frame_count'],'observed_frame_count':len(files),'observed_visual_sequence':observation,'role_review_basis':rolebasis,'judgment_basis':reasoning,'style_basis':'AREA00 승인 원화 및 식별 가능한 기존 MSW VFX 대조. 어두운 재질 경계/중간톤/밝은 코어, 입자·잔광의 단계적 축소가 이어짐. 지역 팔레트/일반·보스 체급 차이는 허용. 복제나 최신 리소스 일치를 요구하지 않음.','visual_evidence':evidence,'previous_review_use':'기존 99개 관찰 기록 참고 + 이번 실제 원본/실제 role PNG 전수 시각 재대조; King/Toy 관찰은 현재 이미지로 교체','preview_review':'실제 Area overview의 몬스터/ICON/프레임 대응 확인. AREA11 라벨 겹침은 별도 기술 항목. 작은 글자 전수 OCR 검사는 아님.','data_state':'승인 SkillTable 후보와 현행 Mislocated 후보 대상행 전체 필드 일치; Maker 등록 상태 미확인','user_decision_needed':'YES: 수정 진행 또는 현행 금지 문구의 예외 승인 선택' if status=='SPEC_MISMATCH' else 'NO','recommended_action':'원화 수정 후보' if status=='SPEC_MISMATCH' else '원화 유지','user_approved':'NO'})
    writecsv('SOURCE_CHECK.csv',sources);writecsv('ART_REVIEW.csv',reviews);dump('CONTRACT_SNAPSHOTS.json',contracts)
    actions=[]
    def action(i,area,mid,role,kind,status,detail,decision,evidence='',blocks=''):
        actions.append({'action_id':i,'area_id':area,'monster_id':mid,'role':role,'action_category':kind,'status':status,'reason_and_next_step':detail,'user_decision_needed':decision,'evidence':evidence,'blocks':blocks,'executed':'NO'})
    action('ART-01','area_11','m_king_bloctopus','PROJECTILE','원화 수정 후보','SPEC_MISMATCH','4장에 분홍 몸통·눈·원형 포구·왕관이 결합. 왕관/블록/각진 에너지 조각은 유지 가능하나 얼굴/본체 표현은 현행 금지와 충돌. 향후 이 역할만 수정 후보. CAST/ICON은 원화 유지.','YES',str(RUN/'evidence/area_11_m_king_bloctopus_comparison.png'),'해당 PROJECTILE 아트 적합성')
    action('EXCEPTION-01','area_11','m_king_bloctopus','PROJECTILE','사용자 예외 승인','OPTION_ONLY','현재 본체형 탄을 유지하려는 경우에만 명세 예외 승인 필요. 현행 명세를 따르는 수정과 대안 관계이며, 현재 예외 승인은 없음.','OPTIONAL',str(RUN/'evidence/area_11_m_king_bloctopus_comparison.png'),'ART-01과 같은 1개 역할; 별도 오류로 중복 집계하지 않음')
    action('TECH-11','area_11','area_package','PREVIEW / metadata','기술적 파일 보정','PENDING_SEPARATE_WORK','원본 HOLD ZIP은 REPACK 완료본이 아님. 기존 기계적 검사에서 남은 명칭/경로/메타데이터 보정을 별도 단계로 유지. 실제 overview에서 ICON/CAST 라벨과 몬스터명·설명 겹침을 확인. 원화 수정 사유가 아니며 이번에는 보정하지 않음.','NO',str(RUN/'evidence/area_11_overview_top_detail.png'),'AREA11 패키지 기술 인계')
    action('TECH-12','area_12','area_package','metadata / package','기술적 파일 보정','PENDING_SEPARATE_WORK','CAST 아트 보류는 해제 가능한 판단이나 원본 ZIP의 기존 기술적 미정리 상태는 남음. 이전 검사에서 제안한 V2.4 패키지 보정을 후속 단계에서 처리. 원화 수정/예외 승인은 불필요.','NO',str(REPACK/'HOLD_AREA_11_12.md'),'AREA12 패키지 기술 인계')
    for i,mid in enumerate(['m_stone_golem','m_bubbling','m_mutant_stone_mask'],1):
        r=next(r for r in RS if r['monster_id']==mid)
        detail='이전 story r5에서 원작 출현지역과의 차이를 제기. 현재 프로젝트 방 배치는 INPUT과 일치하며 원화·스킬 기능의 오류는 없음. 재배치 서사 의도가 별도로 필요할 때만 기획 확인.' if mid!='m_mutant_stone_mask' else '스킬명 발굴지의 석면이 돌의 면/가면을 뜻하는 창작어인지 명칭 의도 확인. 실제 아트는 명세의 돌판/가면 보호 모티브와 일치하므로 원화 수정 사유로 연결하지 않음.'
        action(f'PLAN-{i:02}',r['area_id'],mid,'planning only','지역·명칭 등 기획 확인','NONBLOCKING_PLANNING_QUESTION',detail,'기획 확인',str(ART/'output_audit/runs/20260912_160012_story_skill_coherence_r5/STORY_SKILL_REVIEW.csv'),'아트 적합성 인계는 막지 않음')
    action('RUNTIME-01','all','all','registration / DEF passive / dash attachment','별도 런타임 확인사항','OUT_OF_SCOPE_UNRESOLVED','RootDesk 정식 SkillTable 부재와 Mislocated 후보 등록 문제, DEF 패시브, 돌진 CAST 부착점은 기존 별도 런타임 항목. 후보 데이터 99행은 승인 사본과 일치하나 Maker 등록/실행 성공을 의미하지 않음.','후속 런타임 작업에서 확인',str(RUN/'PROJECT_DATA_CHECK.csv'),'게임 반입·런타임 성공 판정')
    writecsv('ACTION_ITEMS.csv',actions)
    # Restrict style use to visible effects; sparse/near-white thumbnails are not finish evidence.
    style=readcsv(RUN/'STYLE_REFERENCE_CHECK.csv');visible={'0001','0002','0009','0016','0021','0024','0025'}
    for r in style:
        code=r['image_path'].split('/skills/')[1][:4]
        r['review_use']='VISIBLE_VFX_SECONDARY_REFERENCE' if code in visible else 'EXCLUDED_INSUFFICIENT_VISIBLE_DETAIL_IN_THIS_SAMPLE'
        r['visual_basis']='실제 효과의 별형 충격/고리/먹물/전격/불꽃을 식별. 몬스터 본체나 빈 썸네일을 근거로 쓰지 않음.' if code in visible else '이 접촉시트 표본은 흰 배경과 희미한 잔상 위주라 이번 마감 비교의 주 근거에서 제외.'
        r['temporal_limit']='출시/개정 시점 미확인. 최신 공식 스킬 아트로 주장하지 않음.'
    writecsv('STYLE_REFERENCE_CHECK.csv',style)
    preview=readcsv(RUN/'PREVIEW_CHECK.csv')
    for p in preview:
        p['identity_and_assets']='NO_OBVIOUS_ISSUE: 실제 overview와 원본/납품 시트의 형상 대응'
        p['layout_finding']='라벨/몬스터명/설명 겹침; 별도 기술 보정' if p['area_id']=='area_11' else '확인 범위에서 명백한 라벨 오류 없음; 전수 OCR 검사 아님'
        p['evidence']=str(RUN/'boards'/f'preview_review_{(list(selections).index(p["area_id"])//4)+1:02}.png')
    writecsv('PREVIEW_CHECK.csv',preview)
    counts=Counter(r['art_judgment'] for r in reviews);dump('REVIEW_COUNTS.json',{'areas':len(selections),'monster_skill_pairs':len(RS),'role_rows':len(reviews),'role_pngs':sum(len(r['file_hashes']) for r in RS),'source_levels':dict(Counter(r['source_level'] for r in sources)),'art_roles':dict(counts),'style_roles':dict(Counter(r['style_judgment'] for r in reviews)),'pair_no_obvious_issue':98,'pair_spec_mismatch':1,'version_conflicts':0,'input_conflicts_detected':0,'user_approved':False})
    # Hash the exact read-only evidence used, in addition to archive and source hashes.
    evidence_files=[ART/'output_audit/AUDIT_RULES.md',ART/'output_audit/BASELINE_INDEX.csv',ART/'output_audit/BASELINE_OUTPUT_INDEX.csv',REPACK/'REPACK_SUMMARY.md',REPACK/'REVALIDATION.csv',REPACK/'PNG_BYTE_PRESERVATION.csv',REPACK/'HOLD_AREA_11_12.md',OLD/'CONTENT_STYLE_REVIEW.csv',OLD/'REVIEW_STATE.json',OLD/'REUSED_FILE_CHECKS.csv',ART/'output_audit/runs/20260912_160012_story_skill_coherence_r5/STORY_SKILL_REVIEW.csv',ROOT/'RootDesk/MyDesk/GameData/MonsterTable.csv',ROOT/'RootDesk/MyDesk/GameData/AreaTable.csv',ROOT/'RootDesk/MyDesk/GameData/RoomTable.csv',ROOT/'Mislocated/MyDesk/GameData/SkillTable.csv',ART/'images-input-packages-v2_1/INPUT_V2_1_EVIDENCE.zip']
    writecsv('EVIDENCE_INDEX.csv',[{'path':str(p),'sha256':sha(p),'purpose':'read-only audit input'} for p in evidence_files])
    print('ART',dict(counts),'SOURCES',len(sources),'CONTRACTS',len(contracts),'ACTIONS',len(actions))
if __name__=='__main__':main()
