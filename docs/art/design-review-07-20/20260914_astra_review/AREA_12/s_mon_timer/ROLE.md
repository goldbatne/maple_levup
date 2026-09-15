# Runtime role map — 타이머 / 시간 정지 충격

- monster_id: `m_timer`
- skill_id: `s_mon_timer`
- skill_type: `액티브`
- required NEW_ART roles: **ICON | VFX**
- declared current motion: layer_ruids 2개; 타입 animationclip/animationclip; 스타일 clip/clip; 지연 0/0.2초; 지속 0.78/0.88초
- role decision: GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다.
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
