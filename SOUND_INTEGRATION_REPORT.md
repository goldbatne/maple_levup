# VARCO 몬스터 스킬 사운드 연결 보고서

- 기준: VARCO_CODEX_HANDOFF_FINAL.zip의 CODEX_ONE_SHOT_INSTRUCTIONS.md, FINAL_SELECTION_MANIFEST.csv, 원본 WAV 67개.
- 대상: D:/maplestory_levup의 실제 MonsterTable.csv·SkillTable.csv 및 PlayerAttack·MonsterAttack·CompanionCombat·SkillEffect 경로.
- 판정: **정적 연결 67/67, 계정 audioclip 조회 67/67. 실제 67개 자연 전투 청취 검증은 미실행이므로 전체 Runtime PASS는 아님.**
- 2026-10-04 후속: 16개 WAV/OGG를 허용된 trim/fade/제한적 gain으로 보정하고 신규 audioclip 16개에 연결했다. 67개 파일·RUID 정적 검사는 통과했으나 새 Maker Build와 실제 청취는 수행하지 못했다. 문서 맨 아래의 후속 상태표가 이전 파형 판단보다 우선한다.
- Maker 실측: Refresh 성공, Build Error 0 / 기존 Warning 4, Play 후 Runtime Error 0. Maker 서버 _GameData:GetSkill에서 달팽이·파란 달팽이·추억의 신관 및 교정 3종의 새 RUID를 읽음. 추억의 신관 후속음 서버 분배 스모크 로그: memory_monk_followup map=maptown listeners=1. 교정 3종은 Maker Play의 실제 SkillEffect.PlayCast 경로를 호출해 서버 로그에서 새 RUID와 이펙트 생성·종료, Runtime Error 0을 확인했다. 이는 자연 전투 청취 검증과는 구분한다.

## 67개 상세 연결

| 번호 | 몬스터 | 스킬 | SkillID | 최종 WAV | 선택 후보·원본 | RAW → 최종 | 편집 | 최종 RUID | 이벤트·시점 | 연결·검증 | 특이사항 |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 달팽이 | 이슬 미끄럼길 | s_mon_snail_dew_trail | m_snail_s_mon_snail_dew_trail.wav | C2 / Dewdrop_tap_2_82fc32ce.wav | 1.000s → 0.570s | 선행 0.130초·후행 0.300초 정리 | 5fda84e90602476dbb976e6c550fa3c8 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN |  |
| 2 | 파란 달팽이 | 푸른 껍질 | s_mon_blue_snail | m_blue_snail_s_mon_blue_snail.wav | C2 / Shell_buff_2_7485d9c6.wav | 0.750s → 0.700s | 선행 0.050초·후행 0.000초 정리 | 54c985f634a2446197175e7e71622ebe | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN |  |
| 3 | 빨간 달팽이 | 붉은 껍질 돌진 | s_mon_red_snail | m_red_snail_s_mon_red_snail.wav | C2 / Shell_rattle_2_6af7820a.wav | 2.280s → 0.725s | 선행 0.650초·후행 0.905초 정리; 단일 이벤트 발췌 | b4f8d734fd8149a8b890d0bc4339c437 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 4 | 마노 | 마노의 무지개 파동 | s_mon_mano | m_mano_s_mon_mano.wav | C3 / Shell_blast_3_873b3f0a.wav | 2.200s → 1.490s | 선행 0.020초·후행 0.690초 정리 | d3a457ecd67942a4827af853587a8781 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 5 | 주황 버섯 | 포자 살포 | s_mon_mushroom | m_mushroom_s_mon_mushroom.wav | C1 / Spore_pop_1_7d8e165b.wav | 2.230s → 1.595s | 선행 0.050초·후행 0.585초 정리; 단일 이벤트 발췌 | 9e12694af9c4464f94cab3476c4d5aaa | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 6 | 머쉬맘 | 머쉬맘의 포자 충격 | s_mon_mushmom | m_mushmom_s_mon_mushmom.wav | C3 / Mushroom_burst_3_89201472.wav | 6.480s → 1.450s | 선행 0.050초·후행 4.980초 정리; 단일 이벤트 발췌 | 0609421ff0f941d494b6671238c4bdd9 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 7 | 스톤골렘 | 암석 피부 | s_mon_stone | m_stone_golem_s_mon_stone.wav | C2 / Rock_slide_2_847abf4b.wav | 1.760s → 1.305s | 선행 0.040초·후행 0.415초 정리; 단일 이벤트 발췌 | f19bd46e52694cf982a1e45047a56044 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · 청취 NOT_RUN |  |
| 8 | 엑스텀프 | 도끼 휘두르기 | s_mon_axe_stump | m_axe_stump_s_mon_axe_stump.wav | C2 / Axe_chop_2_b0a09bf0.wav | 4.980s → 0.870s | 선행 1.610초·후행 2.500초 정리; 단일 이벤트 발췌 | 84de15eb95004a29a660b9379cd84912 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 9 | 다크 엑스텀프 | 어둠의 뿌리 | s_mon_dark_axe_stump | m_dark_axe_stump_s_mon_dark_axe_stump.wav | C3 / Root_eruption_3_5e3c3192.wav | 2.110s → 1.020s | 선행 0.070초·후행 1.020초 정리 | 836302229aa942dba259f608958657af | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 10 | 와일드보어 | 저돌 맹진 | s_mon_wild_boar | m_wild_boar_s_mon_wild_boar.wav | C2 / Boar_charge_2_02304ea6.wav | 0.690s → 0.570s | 선행 0.040초·후행 0.080초 정리 | 8d97183351f34ccfa51da8be662e8be1 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 11 | 스켈레톤 지휘관 | 뼈 무덤 | s_mon_skeleton_commander | m_skeleton_commander_s_mon_skeleton_commander.wav | C3 / Bone_rattle_3_cea8cc7a.wav | 2.040s → 1.305s | 선행 0.030초·후행 0.705초 정리; 단일 이벤트 발췌 | 3f041b23016d4eaeada4994fc3bc3bb3 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 12 | 파이어보어 | 화염 돌풍 | s_mon_fire_boar | m_fire_boar_s_mon_fire_boar.wav | C1 / Boar_fire_1_f37c1b7f.wav | 0.900s → 0.740s | 선행 0.060초·후행 0.100초 정리 | f583f30017b5465792958511072d9aca | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 13 | 스텀피 | 고목의 생기탄 | s_mon_stumpy | m_stumpy_s_mon_stumpy.wav | C2 / Wood_bolt_2_7907ef66.wav | 4.390s → 1.160s | 선행 0.600초·후행 2.630초 정리; 단일 이벤트 발췌 | 53227b422fed490d97547a907314407d | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 14 | 슬라임 | 끈적한 몸통 | s_mon_slime | m_slime_s_mon_slime.wav | C1 / Slime_slap_1_60e2c61b.wav | 3.180s → 0.600s | 원본 0.05–0.65초에서 핵심 이벤트 재발췌, 양끝 5/80ms fade; 기존 거의 무음 가공본 교정 | 41803b655d514252ae77788dffcd1fbb | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN | 이전 업로드 RUID는 롤백용으로 보존 |
| 15 | 페어리 | 요정의 마법가루 | s_mon_fairy | m_fairy_s_mon_fairy.wav | C2 / Fairy_debuff_2_59aadb24.wav | 3.120s → 1.232s | 선행 0.080초·후행 1.808초 정리; 단일 이벤트 발췌 | 355b54999ec54ece897bcaaa87c59732 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 16 | 다크 스텀프 | 단단한 밑동 | s_mon_dark_stump | m_dark_stump_s_mon_dark_stump.wav | C3 / Tree_shield_3_1da612a7.wav | 4.880s → 0.600s | 원본 0.00–0.60초에서 핵심 이벤트 재발췌, 양끝 5/80ms fade; 기존 거의 무음 가공본 교정 | c5db8f976a6343dc9d9a58c11c64bccc | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN | 이전 업로드 RUID는 롤백용으로 보존 |
| 17 | 파우스트 | 저주의 인형 | s_mon_faust | m_faust_s_mon_faust.wav | C3 / Doll_attack_3_dd80a3c9.wav | 6.680s → 1.305s | 선행 4.710초·후행 0.665초 정리; 단일 이벤트 발췌 | 3b45f087853a471aa788ecf54045493a | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 18 | 옥토퍼스 | 먹물 폭발 | s_mon_octopus | m_octopus_s_mon_octopus.wav | C2 / Ink_spray_2_bcaef0c1.wav | 3.670s → 1.087s | 선행 0.050초·후행 2.533초 정리; 단일 이벤트 발췌 | c684aefa05d847d9ac4fb16dc60beeae | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 19 | 주니어 레이스 | 망령 충격 | s_mon_jr_wraith | m_jr_wraith_s_mon_jr_wraith.wav | C2 / Ghost_wind_2_94de00f3.wav | 6.720s → 1.160s | 선행 0.280초·후행 5.280초 정리; 단일 이벤트 발췌 | b530785b91174bed9e85aaaa86b1082e | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 20 | 셰이드 | 심연의 장막 | s_mon_shade | m_shade_s_mon_shade.wav | C2 / Dark_magic_2_02314e3c.wav | 2.250s → 1.305s | 선행 0.130초·후행 0.815초 정리; 단일 이벤트 발췌 | 327b0031dfd946ef979c045568ff80c5 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · 청취 NOT_RUN |  |
| 21 | 리본 돼지 | 리본 돌진 | s_mon_ribbon_pig | m_ribbon_pig_s_mon_ribbon_pig.wav | C3 / Pig_charge_3_5d5b2630.wav | 3.150s → 0.943s | 선행 0.380초·후행 1.827초 정리; 단일 이벤트 발췌 | ac240ede54764a34828a8184bd9d1f41 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 22 | 불가사리 | 별가시 회전 | s_mon_starfish | m_starfish_s_mon_starfish.wav | C3 / Burst_spine_3_3e019446.wav | 2.530s → 1.087s | 선행 0.140초·후행 1.302초 정리; 단일 이벤트 발췌 | b6b7bb9abe554a6e8f35dbaa9d15fcaf | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 23 | 주니어 발록 | 발록의 화염 파동 | s_mon_jr_balrog | m_jr_balrog_s_mon_jr_balrog.wav | C1 / Fire_strike_1_ff79a8ed.wav | 5.130s → 1.305s | 선행 0.530초·후행 3.295초 정리; 단일 이벤트 발췌 | b1510ab7731a43e3a9e140a8499eacfa | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 24 | 드레이크 | 동굴 용염 | s_mon_drake | m_drake_s_mon_drake.wav | C3 / Dragon_breath_3_00bf3b8e.wav | 2.820s → 1.377s | 선행 0.330초·후행 1.113초 정리; 단일 이벤트 발췌 | fd2791e6dc514498a35d1f2da2a44e1c | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 25 | 와일드카고 | 야수의 그림자 돌진 | s_mon_wild_kargo | m_wild_kargo_s_mon_wild_kargo.wav | C2 / Beast_lunge_2_5743410f.wav | 4.040s → 1.015s | 선행 2.440초·후행 0.585초 정리; 단일 이벤트 발췌 | d9b0cefac67747bfb67a4b77b418c61b | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 26 | 타우로마시스 | 수문장의 낙뢰 | s_mon_tauromacis | m_tauromacis_s_mon_tauromacis.wav | C2 / Lightning_blast_2_abebb9d3.wav | 4.140s → 1.595s | 선행 0.210초·후행 2.335초 정리; 단일 이벤트 발췌 | 304f1c93399d49beac34fbeb5d8925c1 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 27 | 스타픽시 | 별빛 탄환 | s_mon_star_pixie | m_star_pixie_s_mon_star_pixie.wav | C3 / Star_twinkle_3_52273c05.wav | 2.270s → 0.943s | 선행 0.470초·후행 0.858초 정리; 단일 이벤트 발췌 | d8f3d81323b24c2890a745bcdfd54023 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 28 | 루나픽시 | 월광 구슬 | s_mon_lunar_pixie | m_lunar_pixie_s_mon_lunar_pixie.wav | C2 / Moon_chime_2_0fa45004.wav | 2.480s → 0.920s | 선행 0.030초·후행 1.530초 정리 | 749d18409b0e4974a97a4c157f11fe69 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 29 | 엘리쟈 | 여신의 정원 폭풍 | s_mon_eliza | m_eliza_s_mon_eliza.wav | C3 / Leaf_wind_3_b7388123.wav | 4.500s → 1.885s | 선행 0.540초·후행 2.075초 정리; 단일 이벤트 발췌 | 9cdfa177020f41a684cb902092c85bed | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 30 | 헥터 | 설원 늑대 발톱 | s_mon_hector | m_hector_s_mon_hector.wav | C3 / Wolf_lunge_3_297dca4e.wav | 4.180s → 0.800s | 선행 0.070초·후행 3.310초 정리 | 07e0fe37a93540f7b1bcf659e78cb812 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 31 | 화이트팽 | 화이트팽의 빙설 송곳니 | s_mon_white_fang | m_white_fang_s_mon_white_fang.wav | C2 / Ice_snap_2_f1af1837.wav | 3.530s → 0.750s | 원본 0.05–0.80초에서 핵심 이벤트 재발췌, 양끝 5/80ms fade; 기존 거의 무음 가공본 교정 | e0ba0dcfdc664fa3985dd023d92db638 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN | 이전 업로드 RUID는 롤백용으로 보존 |
| 32 | 설산의 마녀 | 추방자의 눈보라 | s_mon_snow_witch | m_snow_witch_s_mon_snow_witch.wav | C1 / Ice_whistle_1_36763186.wav | 3.420s → 1.305s | 선행 1.280초·후행 0.835초 정리; 단일 이벤트 발췌 | a5c723649e444b8fbebef266403291da | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 33 | 스퀴드 | 심해 먹물 폭발 | s_mon_squid | m_squid_s_mon_squid.wav | C2 / Ink_bubble_2_f9cd0ed7.wav | 1.670s → 1.620s | 선행 0.050초·후행 0.000초 정리 | 6d7cbd7d14134c268b7eaf35b27a6df2 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 34 | 샤크 | 포식자의 수류탄 | s_mon_shark | m_shark_s_mon_shark.wav | C1 / Shark_snap_1_79514596.wav | 3.680s → 1.232s | 선행 0.650초·후행 1.798초 정리; 단일 이벤트 발췌 | 1e83860fd97d43df9e9d381e132ed055 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 35 | 피아누스 | 심해왕의 광선 | s_mon_pianus | m_pianus_s_mon_pianus.wav | C3 / Deep_sea_hum_3_b7d2554a.wav | 4.610s → 1.595s | 선행 0.170초·후행 2.845초 정리; 단일 이벤트 발췌 | 81384f58e30e417798e02fe90447d4a2 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 36 | 북치는 토끼 | 태엽 북진동 | s_mon_drumming_bunny | m_drumming_bunny_s_mon_drumming_bunny.wav | C2 / Toy_drumroll_2_ab1226cd.wav | 3.980s → 1.232s | 선행 0.050초·후행 2.697초 정리; 단일 이벤트 발췌 | 2c7f282d2ac54e5ba768aacd57b91d9e | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · 청취 NOT_RUN |  |
| 37 | 킹 블록퍼스 | 왕관 블록탄 | s_mon_king_bloctopus | m_king_bloctopus_s_mon_king_bloctopus.wav | C3 / Toy_blast_3_78496087.wav | 2.740s → 1.160s | 선행 0.250초·후행 1.330초 정리; 단일 이벤트 발췌 | 663bab0325c949d0a21dc4fa699de454 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 38 | 롬바드 | 에오스 중력파 | s_mon_rombot | m_rombot_s_mon_rombot.wav | C2 / Gear_grind_2_c92896e6.wav | 6.040s → 1.450s | 선행 0.030초·후행 4.560초 정리; 단일 이벤트 발췌 | ba73278b8efc4605b06e1c022ef9d65d | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 39 | 장난감 목마 | 태엽 목마 돌진 | s_mon_toy_trojan | m_toy_trojan_s_mon_toy_trojan.wav | C1 / Toy_dash_1_7223676f.wav | 2.370s → 1.087s | 선행 0.360초·후행 0.922초 정리; 단일 이벤트 발췌 | 182c531f26bf4d5fa5cc2de292e420a4 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 40 | 크로노스 | 크로노스의 시간편린 | s_mon_chronos | m_chronos_s_mon_chronos.wav | C3 / Clock_tick_3_464ca4c7.wav | 1.800s → 1.050s | 선행 0.000초·후행 0.750초 정리 | 07fc2aa8ac834a93a792d2b9ef6beedb | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 41 | 타이머 | 시간 정지 충격 | s_mon_timer | m_timer_s_mon_timer.wav | C1 / Time_lock_1_38ae16ac.wav | 5.970s → 1.595s | 선행 1.700초·후행 2.675초 정리; 단일 이벤트 발췌 | 4400e89e84f4445a8136d1a99a94842e | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 42 | 흰 모래토끼 | 사막 굴착탄 | s_mon_white_sand_rabbit | m_white_sand_rabbit_s_mon_white_sand_rabbit.wav | C2 / Rabbit_dig_2_ce61ac14.wav | 5.970s → 1.087s | 선행 1.590초·후행 3.292초 정리; 단일 이벤트 발췌 | c088a1a7581046fcb5dd6eadd43a653a | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 43 | 미요캐츠 | 미요캐츠의 모래매복 | s_mon_meercat | m_meercat_s_mon_meercat.wav | C2 / Sand_burst_2_e377e746.wav | 1.890s → 1.000s | 선행 0.110초·후행 0.780초 정리 | 2e914b18a8954c8091bc66b9ae62994b | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 44 | 데우 | 잠든 선인장의 폭발 | s_mon_deo | m_deo_s_mon_deo.wav | C1 / Cactus_pop_1_df1b9a0d.wav | 5.850s → 1.522s | 선행 0.050초·후행 4.277초 정리; 단일 이벤트 발췌 | 2dc8f3953754423aac177afd88790a72 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 45 | 호문 | 플라스크 독무 | s_mon_homun | m_homun_s_mon_homun.wav | C1 / Flask_uncork_1_5cff2820.wav | 6.110s → 1.740s | 선행 3.100초·후행 1.270초 정리; 단일 이벤트 발췌 | 39df715520da44c3826c27f64c4f129b | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 46 | 로이드 | 알카드노 에너지탄 | s_mon_roid | m_roid_s_mon_roid.wav | C3 / Energy_shot_3_9aca7e7e.wav | 7.930s → 1.015s | 선행 0.000초·후행 6.915초 정리; 단일 이벤트 발췌 | e9825d9ff88240e98ca7800fc5778eef | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 47 | 키메라 | 융합체의 산성 포격 | s_mon_chimera | m_chimera_s_mon_chimera.wav | C2 / Acid_splash_2_47b3bd04.wav | 4.590s → 1.305s | 선행 1.000초·후행 2.285초 정리; 단일 이벤트 발췌 | 0dae6aeb66e54b3c9b7def22431cc15c | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 48 | 킹크랑 | 왕게의 집게 파도 | s_mon_king_clang | m_king_clang_s_mon_king_clang.wav | C1 / Crab_claws_1_0da2a280.wav | 5.790s → 1.232s | 선행 4.250초·후행 0.307초 정리; 단일 이벤트 발췌 | 819066b94fdf4087b8c4cfb6fdfd58be | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 49 | 수련용 나무인형 | 목인 회전타 | s_mon_wooden_dummy | m_wooden_dummy_s_mon_wooden_dummy.wav | C2 / Wood_clack_2_cc74169e.wav | 2.430s → 1.087s | 선행 0.330초·후행 1.012초 정리; 단일 이벤트 발췌 | 66d4a40e6a8f4a6d84ea4bef630e18d6 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 50 | 원공 | 천도 투척 | s_mon_peach_monkey | m_peach_monkey_s_mon_peach_monkey.wav | C3 / Peach_splash_3_a94042fd.wav | 2.480s → 1.087s | 선행 0.240초·후행 1.153초 정리; 단일 이벤트 발췌 | 14d3a607b3d94d39ade456cef0e31137 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 51 | 태륜 | 태륜의 쌍권풍 | s_mon_tae_roon | m_tae_roon_s_mon_tae_roon.wav | C1 / Wind_slice_1_78a4d65b.wav | 3.050s → 1.232s | 선행 0.770초·후행 1.048초 정리; 단일 이벤트 발췌 | f7b5f1a7fa3d400a9921af853583d65b | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 52 | 블러드 하프 | 핏빛 깃울림 | s_mon_blood_harp | m_blood_harp_s_mon_blood_harp.wav | C3 / Feather_twang_3_78f22fe4.wav | 3.740s → 1.160s | 선행 0.060초·후행 2.520초 정리; 단일 이벤트 발췌 | 172c77319116446eb4421f67cf069fe7 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 53 | 블루 와이번 | 빙룡 숨결 | s_mon_blue_wyvern | m_blue_wyvern_s_mon_blue_wyvern.wav | C1 / Ice_breath_1_f7efe383.wav | 2.370s → 1.450s | 선행 0.090초·후행 0.830초 정리; 단일 이벤트 발췌 | 1decd9af92904dd4b8dbb3fa1ec16601 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 54 | 마뇽 | 마뇽의 용화염 | s_mon_manon | m_manon_s_mon_manon.wav | C2 / Dragon_breath_2_39ad6a48.wav | 4.630s → 1.595s | 선행 0.090초·후행 2.945초 정리; 단일 이벤트 발췌 | 201948036fc4452797c6e4c6e84f91f8 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 55 | 추억의 신관 | 추억의 기도파 | s_mon_memory_monk_trainee | m_memory_monk_trainee_s_mon_memory_monk_trainee_cast.wav | C2 / Chime_buff_2_8591e545.wav | 2.510s → 0.970s | 선행 0.020초·후행 1.520초 정리 | 3da9d32bf23f41bfa36cc367bdaecbf6 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 기도 버프 발동 (기존 PlayCast) | 정적 PASS · Maker 데이터 조회 PASS · 청취 NOT_RUN |  |
| 56 | 추억의 신관 | 추억의 기도파 | s_mon_memory_monk_trainee | m_memory_monk_trainee_s_mon_memory_monk_trainee_empowered_hit.wav | C1 / Sacred_impact_1_faae0003.wav | 2.450s → 0.652s | 선행 0.100초·후행 1.698초 정리; 단일 이벤트 발췌 | 879af07877bb4b42b5da9a7a4c51f5ae | 기도 강화가 다음 실제 유효 타격에 소비될 때 (Player·Monster·Companion) | 코드 경로 PASS · Maker RPC 분배 스모크 PASS · 실전 청취 NOT_RUN | 66 SkillID 중 추가 1파일; 시전음과 동시 재생 금지 |
| 57 | 추억의 수호대장 | 시간 수호진 | s_mon_chief_memory_guardian | m_chief_memory_guardian_s_mon_chief_memory_guardian.wav | C1 / Shield_assemble_1_4623626d.wav | 3.080s → 1.305s | 선행 0.110초·후행 1.665초 정리; 단일 이벤트 발췌 | 4809d1d0acb8441eb289c1b3a34c6cd9 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 자기 강화/방어 발동 (기존 PlayCast) | 정적 PASS · 청취 NOT_RUN |  |
| 58 | 도도 | 기억 포식 | s_mon_dodo | m_dodo_s_mon_dodo.wav | C2 / Dark_implosion_2_0fc01834.wav | 5.880s → 1.377s | 선행 0.030초·후행 4.473초 정리; 단일 이벤트 발췌 | 88f8771c975f4cba9d12bd37d01d46d6 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 59 | 마티안 | 마티안 광선탄 | s_mon_mateon | m_mateon_s_mon_mateon.wav | C3 / Alien_ray_3_16dc8b2b.wav | 2.350s → 1.015s | 선행 0.350초·후행 0.985초 정리; 단일 이벤트 발췌 | d6511982ae474b559fee6af15db79f62 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 발사 시작 (기존 PlayProjectile/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 60 | 메카티안 | 기계화 레이저 | s_mon_mecateon | m_mecateon_s_mon_mecateon.wav | C3 / Laser_fire_3_c4f9cb80.wav | 1.200s → 0.800s | 선행 0.040초·후행 0.360초 정리 | 0e6068c7b2994cd9bd01f97127d96317 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 스킬 연출 시작 (기존 PlayCast/PlayAttackAt 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 61 | 제노 | 제노의 중력장 | s_mon_zeno | m_zeno_s_mon_zeno.wav | C1 / Alien_hum_1_2c876942.wav | 8.240s → 1.813s | 선행 0.620초·후행 5.808초 정리; 단일 이벤트 발췌 | 57168ba148724100a3854cd3225f8302 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 62 | 정식기사 C | 기사단 뇌전 연각 | s_mon_official_knight_c | m_official_knight_c_s_mon_official_knight_c.wav | C2 / Electric_dash_2_601cb178.wav | 3.010s → 1.160s | 선행 0.100초·후행 1.750초 정리; 단일 이벤트 발췌 | f0398b3117224b32a83ffded4dbcdc6e | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 63 | 상급기사 B | 상급기사의 이프리트 화염 | s_mon_advanced_knight_b | m_advanced_knight_b_s_mon_advanced_knight_b.wav | C3 / Flame_ignition_3_e7487200.wav | 2.890s → 1.813s | 선행 0.060초·후행 1.018초 정리; 단일 이벤트 발췌 | c028b091bddb4a34abe1ae6e23d07db3 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 64 | 시그너스 | 타락한 여제의 정원 | s_mon_cygnus | m_cygnus_s_mon_cygnus.wav | C1 / Dark_bloom_1_84a8de64.wav | 2.680s → 1.840s | 선행 0.010초·후행 0.830초 정리 | a264d5c56a7c4b87a753bbc8d8e4cb1c | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |
| 65 | 변형된 아이언호그 | 황야의 철갑 돌진 | s_mon_mutant_iron_hog | m_mutant_iron_hog_s_mon_mutant_iron_hog.wav | C2 / Hog_charge_2_e7d6efff.wav | 0.810s → 0.620s | 선행 0.130초·후행 0.060초 정리 | e3d12ef7dd484c438582d3d2432aa25b | SkillTable.sfx_ruid → SkillEffect.ShowCast: 돌진 시작 (기존 PlayDashTravel/PlayCast 경로 확인 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 66 | 에인션트 다크골렘 | 고대 암흑 지진 | s_mon_ancient_dark_golem | m_ancient_dark_golem_s_mon_ancient_dark_golem.wav | C3 / Earthquake_impact_3_a0282276.wav | 4.940s → 1.740s | 선행 0.020초·후행 3.180초 정리; 단일 이벤트 발췌 | cfae6fe60edf437abd4832287b04b847 | SkillTable.sfx_ruid → SkillEffect.ShowCast: 지연 폭발 연출 호출 (실제 타격 정합성 청취 필요) | 정적 PASS · 청취 NOT_RUN |  |
| 67 | 변형된 스텀피 | 검은 뿌리의 묘지 | s_mon_mutant_stumpy | m_mutant_stumpy_s_mon_mutant_stumpy.wav | C3 / Root_lash_3_14e2e07d.wav | 2.040s → 1.700s | 선행 0.070초·후행 0.270초 정리 | d4d75c0e91ab4b138a8b478b19bb1bde | SkillTable.sfx_ruid → SkillEffect.ShowCast: 장판 생성 (기존 PlayAreaAt/PlayCast 경로) | 정적 PASS · 청취 NOT_RUN |  |

## 기술·매핑 검증

- 최종 WAV 67개 / 고유 파일명 67개 / OGG 67개. 모든 WAV는 RIFF PCM 48 kHz, 1채널, 16-bit이고 0 dBFS clipping 샘플은 0개. OGG는 모두 OggS 헤더를 확인했다.
- 매핑 67행, 서로 다른 SkillID 66개. MonsterTable.drop_skill_id 일치 67/67, 실제 SkillTable.sfx_ruid 일치 66/66. 모든 활성 RUID 67개가 계정 audioclip으로 조회되었다.
- 패시브 35개에 신규 SFX 연결 0개. 미사용 s_mon_snail은 기존 값 그대로이며 신규 달팽이 소리는 s_mon_snail_dew_trail에만 연결했다.
- 교정: 다크 스텀프(기존 peak 10 → 26029), 슬라임(447 → 25780), 화이트팽(5273 → 26029). 원본 후보는 바꾸지 않았고 핵심 트랜지언트가 있는 구간만 다시 발췌했다. 세 파일 모두 클리핑 0.
- 기준 WAV: assets/sfx/varco_monster_skills/; Maker용 OGG: assets/sfx/varco_monster_skills_ogg/. 원본 ZIP의 selected_raw/는 변경하지 않았다.
- 길이 조정 폭이 큰 음원(원본 대비 3초 이상 단축)은 22개: m_mushmom_s_mon_mushmom.wav, m_axe_stump_s_mon_axe_stump.wav, m_stumpy_s_mon_stumpy.wav, m_dark_stump_s_mon_dark_stump.wav, m_faust_s_mon_faust.wav, m_jr_wraith_s_mon_jr_wraith.wav, m_jr_balrog_s_mon_jr_balrog.wav, m_wild_kargo_s_mon_wild_kargo.wav, m_hector_s_mon_hector.wav, m_pianus_s_mon_pianus.wav, m_rombot_s_mon_rombot.wav, m_timer_s_mon_timer.wav, m_white_sand_rabbit_s_mon_white_sand_rabbit.wav, m_deo_s_mon_deo.wav, m_homun_s_mon_homun.wav, m_roid_s_mon_roid.wav, m_chimera_s_mon_chimera.wav, m_king_clang_s_mon_king_clang.wav, m_manon_s_mon_manon.wav, m_dodo_s_mon_dodo.wav, m_zeno_s_mon_zeno.wav, m_ancient_dark_golem_s_mon_ancient_dark_golem.wav. 반복 VARCO 이벤트 중 한 이벤트를 발췌한 가공 결과이며, 실제 타이밍 청취는 별도 확인 필요.

## 연결 방식과 변경 파일

- 기존 SkillEffect.ShowCast의 SoundService.PlaySound(skill.sfx_ruid, skill_sfx_volume)를 그대로 사용한다. 플레이어, 몬스터, 동행의 기존 PlayCast/PlayAttackAt 호출에서 66개 기본 발동음이 재생된다. 볼륨 설정은 skill_sfx_volume=0.6이며 이번 작업에서 변경하지 않았다.
- 추억의 신관: 기도 시전음은 SkillTable.sfx_ruid; 강화 타격음은 SkillEffect.PlayMemoryMonkFollowup 한 곳의 RUID가 실제 강화 소비 지점에서 호출된다. 플레이어·몬스터에서는 기존 next-hit 소비 분기, 동행에서는 버프 지속 중 첫 타격의 사운드 전용 플래그를 사용한다. 피해·버프 수치는 변경하지 않았다.
- 변경: Mislocated/MyDesk/GameData/SkillTable.csv; Mislocated/MyDesk/Combat/SkillEffect.mlua, RoomMonster.mlua, CompanionCombat.mlua; Mislocated/MyDesk/PlayerAttack.mlua, MonsterAttack.mlua; 교정 WAV 3개와 OGG 3개; 이 보고서.
- 계정 리소스: 기존 67개를 조회했고, 바이너리 교체 API 완료 단계가 실패한 3개는 **새 교정 리소스 3개를 등록**해 SkillTable을 새 RUID로 바꿨다. 활성 참조는 총 67개. 이전 3개 RUID는 삭제하지 않아 롤백 가능하며 현재 SkillTable에서는 미참조다.
- Maker 리소스 저장소의 account-owned `audioclip` RUID를 참조한다. 공식 Resource Storage 설명은 월드 제작자와 리소스 소유자가 같으면 해당 월드에서 사용할 수 있다고 안내한다. Maker 작업공간에 별도 `Sound` 폴더를 만들거나 OGG 파일을 다시 수동 이동할 필요는 없다. 단, 출시 월드 재생은 이번 Maker 검사로 대체할 수 없다.
- 코드·데이터 변경 전 사본은 C:/Users/dddd/.codex/visualizations/2026/08/30/01a05014-afc4-7e12-839e-e3f24707e98b/rollback-pr188-20261003/sound-reattempt-20261004/ 에 보존했다.

## 우선 36개 후속 검증 (2026-10-04)

판정 범위는 이 표의 36개다. **LISTEN_PASS 0 / LISTEN_FAIL 0 / NOT_TESTABLE 36.** Maker 제어 도구는 Play·스크린샷·로그를 제공하지만 게임 오디오 녹음/청취 입력은 제공하지 않는다. Windows 캡처 장치 조회에서도 오디오 입력 장치가 열거되지 않았고, 이 세션은 전달된 WAV의 오디오 입력을 지원하지 않았다. 따라서 서버 시전 로그나 파형 측정을 청취 결과로 바꾸지 않았다. 자연 전투의 Player·MONSTER_SKILL·동행별 청취도 수행하지 못했다.

아래의 시간은 코드와 최종 48 kHz WAV 파형의 **정적 측정**이다. 시작/피크는 10 ms RMS 창의 최대값 대비 임계값으로 찾은 값이며 실제로 들리는 순간을 확정하지 않는다. 지연 폭발 피해 시점은 시전 후 0.55초, 돌진 도착 피해는 약 0.20초, 투사체 피해는 약 0.35초다. 장판 첫 피해는 0.15초이고 이후 0.45초 간격이다.

| 번호 | SkillID | 코드·파형 확인과 남은 청취 판단 | 상태 |
|---:|---|---|---|
| 3 | s_mon_red_snail | 일반 돌진은 이동 시작에서 PlayCast. 0.72초 클립의 피크 0.52초; 도착 0.20초와 실제 충격 청취 비교 필요. | NOT_TESTABLE |
| 6 | s_mon_mushmom | 즉시 공격 PlayAttackAt. 6.48초 원본에서 1.45초 선택; 반복 구간 선택과 타격감 청취 필요. | NOT_TESTABLE |
| 8 | s_mon_axe_stump | 즉시 전방 타격인데 0.87초 클립의 큰 에너지 시작 0.77초. 지연 체감 위험이 높으며 4.98초 원본의 선택 구간 청취 필요. 임의 재편집 안 함. | NOT_TESTABLE |
| 9 | s_mon_dark_axe_stump | PlayAreaAt는 시전 순간 사운드, 피해는 0.55초 뒤. 클립 피크 0.41초; 실제 충격 일치 청취 필요. | NOT_TESTABLE |
| 10 | s_mon_wild_boar | 일반 돌진 PlayCast는 이동 시작. 클립 피크 0.15초, 도착 약 0.20초. | NOT_TESTABLE |
| 13 | s_mon_stumpy | PlayProjectile 발사 시 사운드, 피해 약 0.35초 뒤. 4.39초 원본에서 1.16초 선택; 피크 1.01초의 의미 청취 필요. | NOT_TESTABLE |
| 14 | s_mon_slime | 교정 WAV 피크 -2.1 dBFS, RMS -26.7 dBFS. Maker PlayCast RUID 조회/이펙트 경로는 통과했지만 실제 믹스에서 들리는지는 미확인. | NOT_TESTABLE |
| 16 | s_mon_dark_stump | 교정 WAV 피크 -2.0 dBFS, RMS -18.2 dBFS. Maker PlayCast 경로 통과; 실제 방어 시전 청취 필요. | NOT_TESTABLE |
| 17 | s_mon_faust | 투사체 발사음. WAV RMS -42.8 dBFS로 낮아 실제 믹스에서 묻힐 위험이 있다. 6.68초 원본 선택 구간 청취 필요. | NOT_TESTABLE |
| 19 | s_mon_jr_wraith | 즉시 전방 타격. 6.72초 원본에서 1.16초 선택; 피크 0.97초로 늦어 실제 체감 확인 필요. | NOT_TESTABLE |
| 21 | s_mon_ribbon_pig | 일반 돌진 PlayCast는 이동 시작. 클립 피크 0.48초로 도착 약 0.20초보다 늦다. | NOT_TESTABLE |
| 23 | s_mon_jr_balrog | 전방 타격 PlayAttackAt. 5.13초 원본에서 1.30초 선택; 피크 0.79초의 타격 의미 확인 필요. | NOT_TESTABLE |
| 25 | s_mon_wild_kargo | 일반 돌진 PlayCast는 이동 시작. 클립 큰 에너지 시작 0.34초/피크 0.90초, 도착 약 0.20초와 청취 비교 필요. | NOT_TESTABLE |
| 26 | s_mon_tauromacis | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 0.90초; 충격이 늦게 들릴 위험. | NOT_TESTABLE |
| 30 | s_mon_hector | 일반 돌진 PlayCast는 이동 시작. 클립 피크 0.53초, 도착 약 0.20초. | NOT_TESTABLE |
| 31 | s_mon_white_fang | 교정 WAV 피크 -2.0 dBFS, RMS -20.9 dBFS. Maker PlayCast 경로 통과; 실제 전방 타격 청취 필요. | NOT_TESTABLE |
| 35 | s_mon_pianus | 즉시 직선 타격. 4.61초 원본에서 1.59초 선택; 피크 1.39초가 실제 타격보다 늦게 들리는지 확인 필요. | NOT_TESTABLE |
| 38 | s_mon_rombot | 즉시 중심 타격. 6.04초 원본에서 1.45초 선택; 피크 0.08초. 반복 구간 선택 청취 필요. | NOT_TESTABLE |
| 39 | s_mon_toy_trojan | 일반 돌진 PlayCast는 이동 시작. 클립 피크 1.00초, 도착 약 0.20초. | NOT_TESTABLE |
| 40 | s_mon_chronos | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 0.45초; 청취 타이밍 확인 필요. | NOT_TESTABLE |
| 41 | s_mon_timer | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 0.62초로 정적상 가깝지만 청취 미확인. | NOT_TESTABLE |
| 42 | s_mon_white_sand_rabbit | 즉시 직선 타격인데 1.09초 클립의 큰 에너지 시작 0.83초. 5.97초 원본 선택 구간/타격 지연 체감 확인 필요. | NOT_TESTABLE |
| 43 | s_mon_meercat | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 0.38초. | NOT_TESTABLE |
| 44 | s_mon_deo | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 0.11초라 충격이 선행할 위험; 5.85초 원본 선택 구간 확인 필요. | NOT_TESTABLE |
| 45 | s_mon_homun | 장판 생성 때 사운드 1회, 피해 0.15/0.60/1.05초. 1.74초 클립이 지속 펄스처럼 들리는지 확인 필요. | NOT_TESTABLE |
| 46 | s_mon_roid | 투사체 발사 시 사운드, 피해 약 0.35초. WAV 피크 -16.3 dBFS/RMS -32.3 dBFS라 믹스에서 묻히는지 확인 필요. | NOT_TESTABLE |
| 47 | s_mon_chimera | 3갈래 발사체가 같은 음원을 3회 겹쳐 호출하던 경로를 시전당 1회로 수정. Maker 로그: 투사체 3개 생성, projectile_launch 1회, Error 0. 자연 전투 청취는 미확인. | NOT_TESTABLE |
| 48 | s_mon_king_clang | 즉시 전방 타격인데 1.23초 클립의 큰 에너지 시작 0.90초. 5.79초 원본 선택 구간/타격 지연 체감 확인 필요. | NOT_TESTABLE |
| 54 | s_mon_manon | 즉시 전방 타격. 4.63초 원본에서 1.59초 선택; 피크 0.48초의 실제 의미 확인 필요. | NOT_TESTABLE |
| 55 | s_mon_memory_monk_trainee | cast는 BUFF 적용 직후 PlayCast, 0.97초 클립. 강화타격 사운드 호출은 이 분기에 없음. 청취 구분 미확인. | NOT_TESTABLE |
| 56 | s_mon_memory_monk_trainee | empowered_hit은 Player/Monster의 유효 타격 소비 분기, 동행의 첫 피해 계산 분기에서 별도 호출. 코드상 cast와 동시 호출되지 않으나 실제 간격/청취 미확인. | NOT_TESTABLE |
| 58 | s_mon_dodo | 투사체 발사 시 사운드, 피해 약 0.35초. 5.88초 원본에서 1.38초 선택; 피크 0.98초 의미 확인 필요. | NOT_TESTABLE |
| 61 | s_mon_zeno | 장판 생성 때 사운드 1회, 피해 0.15/0.60/1.05초. 8.24초 원본에서 1.81초 선택; 피크 1.13초의 지속감 확인 필요. | NOT_TESTABLE |
| 62 | s_mon_official_knight_c | **정적 결함 수정:** 전용 이동 VFX 분기가 PlayCast를 건너뛰어 무음이던 상태. 이동 VFX 시작에서 ShowCast 음향만 전달. Maker 로그 dash_begin listeners=1, Build Error 0/Runtime Error 0. 실제 청취 미확인. | NOT_TESTABLE |
| 65 | s_mon_mutant_iron_hog | 일반 돌진 PlayCast는 이동 시작. 클립 피크 0.30초, 도착 약 0.20초. | NOT_TESTABLE |
| 66 | s_mon_ancient_dark_golem | PlayAreaAt 사운드 즉시, 피해 0.55초. 클립 피크 1.15초라 늦게 들릴 위험; 4.94초 원본 선택 구간 확인 필요. | NOT_TESTABLE |

### 이 검증에서 확인한 수정과 근거

- **62번 이벤트 연결:** SkillEffect.PlayDashTravelIfNeeded가 정식기사 C에서 true를 반환하면 PlayerAttack·MonsterAttack·CompanionCombat 모두 일반 PlayCast를 호출하지 않았다. 기존 WAV나 VFX/돌진 시간을 바꾸지 않고, 그 분기에서 ShowCast의 사운드만 현 맵 사용자에게 전달했다. Maker에서 `[SkillSFX] dash_begin s_mon_official_knight_c listeners=1`과 이동 이펙트 생성/종료를 확인했다. 이는 전달 요청의 실행 증거이지 사람이 소리를 들었다는 증거는 아니다.
- **47번 중첩 음향:** 세 갈래 투사체마다 PlayProjectile이 ShowCast를 호출해 같은 발사음이 한 시전에 세 번 겹칠 수 있었다. Player·Monster·Companion 호출부에서 첫 성공 투사체에만 음향을 전달하고 발사체 3개/VFX/피해 시점은 유지했다. Maker 로그에서 투사체 생성 3회, `[SkillSFX] projectile_launch s_mon_chimera` 1회를 확인했다.
- **파형 위험만 발견, 음원 수정 안 함:** 8·42·48번의 큰 에너지는 각각 클립 시작 약 0.77·0.83·0.90초 뒤다. 즉시 타격과 청각적으로 어긋날 가능성이 있지만, 부드러운 선행음인지 잘못 선택한 반복 구간인지는 실제 청취 없이 판정할 수 없다. 17·46번은 RMS가 낮아 실제 게임 믹스 청취가 필요하다. 이 5개와 지연 폭발 7개를 추정으로 재편집하거나 피해/VFX 시간을 변경하지 않았다.
- **검증 범위:** Maker Refresh/Build Error 0, 기존 Warning 4, 이번 스모크 Play Runtime Error 0. 직접 RPC 스모크와 코드/파형 검사는 자연 전투 청취와 별도다.

## 미검증·주의

- **NOT_RUN:** 67개 각각의 실제 자연 전투 청취, Player/MONSTER_SKILL/동행 전 타입별 타이밍, 돌진·투사체·지연 폭발·장판의 청각적 동기, 보스 청취. Maker RPC 스모크는 해당 전투 검증을 대신하지 않는다.
- **작업공간 구조 이상:** 이번 사운드 편집 전부터 RootDesk/MyDesk가 디스크에서 없어지고 대응 파일 상당수가 Mislocated/MyDesk에 있는 상태를 확인했다. Maker Play는 이 위치의 SkillTable과 수정 코드를 읽고 빌드했지만 Git에는 RootDesk의 대량 삭제와 Mislocated의 미추적 파일이 보인다. 구조 전체 이동·삭제·재시작은 수행하지 않았다. 이 상태에서는 사운드 작업만 분리한 안전한 커밋/PR을 만들 수 없으므로 먼저 Maker 워크스페이스 경로를 별도 복구·검증해야 한다.
- 계정 리소스 갱신 시도 중 업로드된 임시 바이너리 하나는 갱신 완료 API 오류로 기존 RUID에 반영되지 않았다. 게임 참조에는 사용하지 않는다.
- commit/push 없음. 기존 맵·UI·타일·전투 수치·쿨다운·VFX는 변경하지 않았다.

## 파형 기반 타이밍 보정 (2026-10-04, 후속 작업)

이 절은 위의 **보정 전** 파형 판단을 갱신한다. 청취 장치나 Maker 제어 도구가 이번 세션에 제공되지 않아 `LISTEN_PASS`는 0개이며, 우선 36개는 계속 `NOT_TESTABLE`이다. 기존 WAV의 선택 후보와 파일명은 유지했고 선행 무음·불필요한 꼬리, 5 ms 안팎의 클릭 방지 fade만 조정했다. 예외적으로 파우스트와 로이드는 음량을 각각 +6 dB, +8 dB 올렸다. pitch, time-stretch, 합성, 스킬 피해·VFX·이동 타이밍은 변경하지 않았다.

측정값은 WAV 48 kHz PCM의 10 ms RMS 창 기준이다. `첫 신호`는 해당 클립 최대 RMS의 10% 또는 -44 dBFS 중 큰 문턱을 처음 넘는 지점이며, `주 피크`는 최대 RMS 창이다. 청감상의 타격 시점과 동의어는 아니다. 보정 전 WAV·OGG 및 SkillTable·보고서 사본은 `docs/reports/sound-waveform-timing-20261004/originals/`에 보존했다. 기존 RUID의 바이너리 교체 API는 업로드 후 완료 단계에서 실패하여, **새 audioclip 16개를 등록하고 SkillTable의 해당 RUID만 변경**했다. 기존 리소스는 삭제하지 않았다.

| 번호 | 파일 | 길이 전→후 (초) | 첫 신호 전→후 (초) | 주 피크 전→후 (초) | 맞춘 이벤트·남은 한계 | Gain | RUID 전→후 | 파형 판정 |
|---:|---|---:|---:|---:|---|---:|---|---|
| 6 | `m_mushmom_s_mon_mushmom.wav` | 1.450→0.350 | 0.03→0.03 | 0.05→0.05 | 즉시 타격, 1초 이상 거의 무음인 꼬리 제거 | 0 dB | `20461fa582ff42af94257cf917626769`→`0609421ff0f941d494b6671238c4bdd9` | WAVEFORM_TIMING_PASS |
| 8 | `m_axe_stump_s_mon_axe_stump.wav` | 0.870→0.150 | 0.77→0.05 | 0.83→0.11 | 즉시 도끼 타격의 긴 선행 무음 제거 | 0 dB | `94d06c4757ff48c1afc5407f66ce8e75`→`84de15eb95004a29a660b9379cd84912` | WAVEFORM_TIMING_PASS |
| 17 | `m_faust_s_mon_faust.wav` | 1.305→0.460 | 0.14→0.14 | 0.14→0.14 | 투사체 발사음 뒤의 긴 무음 제거 | +6 dB | `0116e700bf02422eb81361f48a189a8d`→`3b45f087853a471aa788ecf54045493a` | WAVEFORM_TIMING_PASS |
| 20 | `m_shade_s_mon_shade.wav` | 1.305→1.055 | 0.33→0.08 | 0.80→0.55 | 자기 방어 발동 시작 cue를 앞당김, 형성 tail 유지 | 0 dB | `508cecc6fdcb4e45908a39fdee7d951b`→`327b0031dfd946ef979c045568ff80c5` | WAVEFORM_TIMING_PASS |
| 21 | `m_ribbon_pig_s_mon_ribbon_pig.wav` | 0.943→0.863 | 0.12→0.04 | 0.48→0.40 | 돌진 출발음만 정렬. 도착 충격은 0.20초보다 늦어 청취 필요 | 0 dB | `68b7a80b374a481c9b51d7b20841df4e`→`ac240ede54764a34828a8184bd9d1f41` | WAVEFORM_TIMING_LIMITED |
| 25 | `m_wild_kargo_s_mon_wild_kargo.wav` | 1.015→0.745 | 0.34→0.07 | 0.90→0.63 | 돌진 출발음 정렬. 충격을 0.20초에 맞추려면 출발음을 훼손하므로 유지 | 0 dB | `a8a875e6147f4afeb2e371dc159813f6`→`d9b0cefac67747bfb67a4b77b418c61b` | WAVEFORM_TIMING_LIMITED |
| 32 | `m_snow_witch_s_mon_snow_witch.wav` | 1.305→0.605 | 0.76→0.05 | 1.26→0.56 | 직선 공격의 긴 선행 무음 제거. 후반 에너지가 실제 타격인지 청취 필요 | 0 dB | `16f7384d08d84a90865afacf19a3c713`→`a5c723649e444b8fbebef266403291da` | WAVEFORM_TIMING_LIMITED |
| 37 | `m_king_bloctopus_s_mon_king_bloctopus.wav` | 1.160→1.000 | 0.22→0.06 | 0.33→0.17 | 투사체 발사 cue 정렬, 피해 0.35초는 그대로 | 0 dB | `ea2dc409052d477590016334457a12ef`→`663bab0325c949d0a21dc4fa699de454` | WAVEFORM_TIMING_PASS |
| 41 | `m_timer_s_mon_timer.wav` | 1.595→1.525 | 0.23→0.16 | 0.62→0.55 | 지연 폭발의 강한 파형을 피해 약 0.55초에 정렬, 앞선 경고음 유지 | 0 dB | `ed6f0d55ce004747ace9faeba70c101a`→`4400e89e84f4445a8136d1a99a94842e` | WAVEFORM_TIMING_PASS |
| 42 | `m_white_sand_rabbit_s_mon_white_sand_rabbit.wav` | 1.087→0.317 | 0.01→0.06 | 0.92→0.15 | 앞부분의 극히 약한 잔여 신호를 제거해 즉시 타격에 맞춤 | 0 dB | `ba05265e00074fbe82c562ddf058d235`→`c088a1a7581046fcb5dd6eadd43a653a` | WAVEFORM_TIMING_PASS |
| 44 | `m_deo_s_mon_deo.wav` | 1.522→0.470 | 0.02→0.02 | 0.11→0.11 | 1초 이상의 무음 꼬리만 제거. 피크가 지연 폭발 피해 0.55초보다 앞서는 문제는 trim으로 고칠 수 없음 | 0 dB | `fc08b4f92a95464180132aef07fabdf7`→`2dc8f3953754423aac177afd88790a72` | WAVEFORM_TIMING_LIMITED |
| 45 | `m_homun_s_mon_homun.wav` | 1.740→1.500 | 0.29→0.05 | 0.43→0.19 | 장판 생성 cue와 첫 피해 약 0.15초에 접근, 후속 지속음 보존 | 0 dB | `d84599dd70624a36995b6f3720972899`→`39df715520da44c3826c27f64c4f129b` | WAVEFORM_TIMING_PASS |
| 46 | `m_roid_s_mon_roid.wav` | 1.015→1.015 | 0.00→0.00 | 0.02→0.02 | 투사체 발사 위치 유지, 지나치게 낮은 음량만 보정 | +8 dB | `15ed7f06bfc24930b74d23f370b2f502`→`e9825d9ff88240e98ca7800fc5778eef` | WAVEFORM_TIMING_PASS |
| 48 | `m_king_clang_s_mon_king_clang.wav` | 1.232→0.482 | 0.80→0.05 | 0.92→0.17 | 즉시 타격의 긴 선행 무음 제거 | 0 dB | `060738b647364b7b9f2dcf9ffd38eb24`→`819066b94fdf4087b8c4cfb6fdfd58be` | WAVEFORM_TIMING_PASS |
| 50 | `m_peach_monkey_s_mon_peach_monkey.wav` | 1.087→0.800 | 0.02→0.02 | 0.16→0.16 | 투사체 발사 뒤 무의미한 꼬리 제거 | 0 dB | `61c85289a05b48acaf04d9bb7d84cc83`→`14d3a607b3d94d39ade456cef0e31137` | WAVEFORM_TIMING_PASS |
| 65 | `m_mutant_iron_hog_s_mon_mutant_iron_hog.wav` | 0.620→0.540 | 0.11→0.03 | 0.30→0.22 | 돌진 출발·약 0.20초 도착 충격에 정렬 | 0 dB | `530873d3f4f3403d906ab8d15612316f`→`e3d12ef7dd484c438582d3d2432aa25b` | WAVEFORM_TIMING_PASS |

### 변경하지 않은 우선 대상과 제한

- 3·10·30·39·62번 돌진은 시작 신호가 이미 0초 부근에 있다. 특히 62번은 이동 경로 VFX가 일반 `PlayCast`를 건너뛰고 이동 시작에서 `ShowCast`로 소리를 내는 코드 경로를 재확인했다. 3·30·39·62번의 늦은 최대 피크를 0.20초로 당기면 선행 이동음을 잃으므로 음원과 이동 코드를 유지했다.
- 9·26·40·43·66번 지연 폭발은 경고/형성 소리가 앞에 있다. 9·40·43번은 주 피크가 피해보다 다소 빠르고, 26·66번은 늦다. 전자를 trim으로 뒤로 미룰 수 없고 후자를 크게 자르면 경고음을 잃는다. 44번도 같은 구조적 한계가 남는다. **실제 충격 청취 검증 전에는 이들을 완전 정합으로 판정하지 않는다.**
- 13·58번 투사체의 늦은 최대 피크는 비행/잔향일 수 있다. `PlayProjectile`의 음향은 발사 시 한 번 나오며 피해는 별도 타이머로 약 0.35초 뒤 발생한다. 피해 피크를 억지로 맞추기 위해 발사음을 잘라내지 않았다. 47번 3갈래 음향은 기존의 시전당 1회 수정 상태를 유지했다.
- 19·23·35·54번 즉시 공격은 초반부터 유의미한 바람·불꽃·빔·호흡 에너지가 이어져 늦은 주 피크만을 기준으로 자르지 않았다. 14·16·31번은 이전 저음량 교정본을 그대로 보존했다. 55 cast와 56 empowered_hit은 다른 파일·이벤트로 유지했다. 5·29·33·61·63·64·67번 장판도 후속 펄스 훼손 위험 때문에 유지했다.

### 전수 정적 검사와 실제 미검증

- 최종 파일: WAV 67개, OGG 67개. WAV 전부 48 kHz·mono·16-bit PCM, clipped sample 0. OGG 67개 전부 디코딩 성공.
- 연결: 보고서 67행/66 고유 SkillID/67 고유 WAV/67 고유 RUID. SkillTable의 일반 스킬 66개와 `SkillEffect.MemoryMonkFollowupSfxRuid`의 56번을 각각 대조했고 누락 0. 신규 RUID 16개는 계정 `audioclip` 메타데이터 조회 성공.
- 코드 경로: PlayerAttack·MonsterAttack·CompanionCombat의 `PlayAttackAt`/`PlayAreaAt`/`PlayProjectile`/`PlayDashTravelIfNeeded`/`PlayCast`와 `SkillEffect.ShowCast`의 `_SoundService:PlaySound` 연결을 확인. 게임 코드·VFX·피해·이동 시간은 이번 작업에서 수정하지 않음.
- **청취:** 우선 36개 전부 `NOT_TESTABLE` 유지. `WAVEFORM_TIMING_PASS`는 파형·코드 정적 판정이며 `LISTEN_PASS`가 아니다. Maker Refresh/Build/Play 제어 도구가 이번 세션에 노출되지 않아 새 빌드·런타임 결과도 `NOT_RUN`이다. 위쪽의 이전 Maker 결과를 이번 보정본의 결과로 재사용하지 않는다.
- 남은 한계: 21·25번 돌진 도착음, 32번 직선 공격의 늦은 피크, 44번 및 일부 지연 폭발의 이른/늦은 충격은 허용된 trim만으로 출발·경고음과 충격을 동시에 맞출 수 없다. 청취가 가능할 때 우선 재검증해야 한다.
- RootDesk/MyDesk와 Mislocated/MyDesk의 기존 구조 문제는 이동·삭제·복구하지 않았다. commit/push하지 않았다.

### 우선 36개 최종 상태표

`WAVEFORM_TIMING_LIMITED`는 제공된 trim/fade/gain만으로 경고음·이동음과 충격 피크를 동시에 맞출 수 없거나, 파형만으로 피크의 의미를 가릴 수 없는 경우다. 청취 판정은 36개 전부 `NOT_TESTABLE`이다.

| 번호 | 파형·코드 판정 | 청취 |
|---:|---|---|
| 3 | WAVEFORM_TIMING_LIMITED — 출발음 유지, 도착 피크 늦음 | NOT_TESTABLE |
| 6 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 8 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 9 | WAVEFORM_TIMING_LIMITED — 충격 피크가 피해보다 빠름 | NOT_TESTABLE |
| 10 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 13 | WAVEFORM_TIMING_LIMITED — 발사음은 초반, 늦은 피크 의미 미확인 | NOT_TESTABLE |
| 14 | WAVEFORM_TIMING_PASS — 기존 교정본 유지 | NOT_TESTABLE |
| 16 | WAVEFORM_TIMING_PASS — 기존 교정본 유지 | NOT_TESTABLE |
| 17 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 19 | WAVEFORM_TIMING_LIMITED — 초반 유령 바람과 늦은 피크 구분 불가 | NOT_TESTABLE |
| 21 | WAVEFORM_TIMING_LIMITED — 출발음 정렬, 도착 피크 늦음 | NOT_TESTABLE |
| 23 | WAVEFORM_TIMING_LIMITED — 초반 화염과 늦은 피크 구분 불가 | NOT_TESTABLE |
| 25 | WAVEFORM_TIMING_LIMITED — 출발음 정렬, 도착 피크 늦음 | NOT_TESTABLE |
| 26 | WAVEFORM_TIMING_LIMITED — 경고음 유지, 충격 피크 늦음 | NOT_TESTABLE |
| 30 | WAVEFORM_TIMING_LIMITED — 출발음 유지, 도착 피크 늦음 | NOT_TESTABLE |
| 31 | WAVEFORM_TIMING_PASS — 기존 교정본 유지 | NOT_TESTABLE |
| 35 | WAVEFORM_TIMING_LIMITED — 초반 빔 준비와 늦은 피크 구분 불가 | NOT_TESTABLE |
| 38 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 39 | WAVEFORM_TIMING_LIMITED — 출발음 유지, 도착 피크 늦음 | NOT_TESTABLE |
| 40 | WAVEFORM_TIMING_PASS — 피해 0.55초에 근접한 0.45초 피크 | NOT_TESTABLE |
| 41 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 42 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 43 | WAVEFORM_TIMING_LIMITED — 충격 피크가 피해보다 빠름 | NOT_TESTABLE |
| 44 | WAVEFORM_TIMING_LIMITED — trim으로 충격 피크를 뒤로 보낼 수 없음 | NOT_TESTABLE |
| 45 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 46 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 47 | WAVEFORM_TIMING_PASS — 시전당 발사음 1회 연결 유지 | NOT_TESTABLE |
| 48 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 54 | WAVEFORM_TIMING_LIMITED — 초반 브레스와 늦은 피크 구분 불가 | NOT_TESTABLE |
| 55 | WAVEFORM_TIMING_PASS — cast 별도 파일·이벤트 | NOT_TESTABLE |
| 56 | WAVEFORM_TIMING_PASS — empowered_hit 별도 파일·이벤트 | NOT_TESTABLE |
| 58 | WAVEFORM_TIMING_LIMITED — 발사음은 초반, 늦은 피크 의미 미확인 | NOT_TESTABLE |
| 61 | WAVEFORM_TIMING_LIMITED — 후속 장판 펄스 청감 미확인 | NOT_TESTABLE |
| 62 | WAVEFORM_TIMING_LIMITED — 이동 시작음 연결, 도착 피크 늦음 | NOT_TESTABLE |
| 65 | WAVEFORM_TIMING_PASS | NOT_TESTABLE |
| 66 | WAVEFORM_TIMING_LIMITED — 경고음 유지, 충격 피크 늦음 | NOT_TESTABLE |

## 최종 Maker 검증 상태 및 PR 범위 (2026-10-04)

이 절은 위쪽의 **보정 이전** Maker 성공 기록보다 최신 상태를 나타낸다. 최종 파형 보정본에 대한 Maker 제어 연결이 제공되지 않아 Refresh, Build, Play를 다시 실행하지 못했다. 이전 Build Error 0 / Warning 4 / Runtime Error 0을 최종 보정본의 결과로 재사용하지 않는다.

| 검사 | 최종 상태 |
|---|---|
| STATIC_MAPPING | PASS — 일반 SkillID 66개와 별도 강화 타격 1개 |
| WAV_VALIDATION | PASS — 67/67 |
| OGG_VALIDATION | PASS — 67/67 |
| AUDIOCLIP_RUID | PASS — 67/67 정적·계정 리소스 조회 |
| NEW_AUDIOCLIP_RUID | PASS — 16/16 정적·계정 리소스 조회 |
| MAKER_REFRESH | NOT_RUN — 최종 보정본 미실행 |
| MAKER_BUILD | NOT_RUN — Error/Warning 수 확인 불가 |
| MAKER_RUNTIME_SMOKE | NOT_RUN — Runtime Error 수 확인 불가 |
| WAVEFORM_TIMING | PASS 18 / LIMITED 18 |
| LISTEN_VALIDATION | NOT_TESTABLE — 36개 우선 항목 포함 자연 전투 청취 미실행 |

PR에는 Git이 원래 추적하던 `RootDesk/MyDesk` 경로의 사운드 코드 변경 4개, `Mislocated/MyDesk/GameData/SkillTable.csv`의 RUID 갱신, 최종 WAV/OGG 67쌍, 이 보고서와 보정 전 증거만 담는다. Maker가 만든 작업공간의 대량 이동·삭제는 커밋에 포함하지 않는다. PR은 정적 연결 변경의 검토용이며 최종 Maker 기술 검증이나 청취 완료를 뜻하지 않는다.
