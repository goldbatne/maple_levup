# Runtime role map — 태륜 / 태륜의 쌍권풍

- monster_id: `m_tae_roon`
- skill_id: `s_mon_tae_roon`
- skill_type: `액티브`
- required NEW_ART roles: **ICON | VFX | PROJECTILE_READING**
- declared current motion: layer_ruids 2개; 타입 animationclip/animationclip; 스타일 clip/clip; 지연 0/0.2초; 지속 0.75/0.85초; 투사체 5328a3875a32437784c949579f259a00가 목표 방향으로 이동
- role decision: GENERATION_SPEC의 frame-separated VFX와 기본 ICON이 필수 NEW_ART다.
- PROJECTILE_READING은 투사체 진행 방향과 충돌점 읽힘을 VFX 프레임 안에서 보존한다. 별도 파일은 GENERATION_SPEC가 명시할 때만 만든다.
- base ICON is 256x256 RGBA. disabled/mouseover variants are not required by this INPUT.
- game scale, offset, RUID, AnimationClip settings are outside this image-production package and must not be changed.
