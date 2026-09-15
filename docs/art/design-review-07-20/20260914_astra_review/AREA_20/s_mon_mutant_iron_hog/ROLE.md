# Runtime role map — 변형된 아이언호그 / 황야의 철갑 돌진

- monster_id: `m_mutant_iron_hog`
- skill_id: `s_mon_mutant_iron_hog`
- skill_type: `액티브`
- required NEW_ART roles: **ICON | VFX**
- declared current motion: layer_ruids 2개; 타입 animationclip/animationclip; 스타일 clip/clip; 지연 0/.18초; 지속 .68/.78초; 시전자가 목표 방향으로 돌진
- role decision: GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다.
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
