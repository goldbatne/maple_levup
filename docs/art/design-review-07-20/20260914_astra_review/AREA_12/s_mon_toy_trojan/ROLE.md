# Runtime role map — 장난감 목마 / 태엽 목마 돌진

- monster_id: `m_toy_trojan`
- skill_id: `s_mon_toy_trojan`
- skill_type: `액티브`
- required NEW_ART roles: **ICON | VFX**
- declared current motion: layer_ruids 1개; 타입 animationclip; 스타일 clip; 지연 0초; 지속 0.7초; 시전자가 목표 방향으로 돌진
- role decision: GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다.
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
