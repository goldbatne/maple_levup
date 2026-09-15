# Runtime role map — 스퀴드 / 심해 먹물 폭발

- monster_id: `m_squid`
- skill_id: `s_mon_squid`
- skill_type: `액티브`
- required NEW_ART roles: **ICON | VFX**
- declared current motion: layer_ruids 1개; 타입 animationclip; 스타일 clip; 지연 0.12초; 지속 0.82초
- role decision: GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다.
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
