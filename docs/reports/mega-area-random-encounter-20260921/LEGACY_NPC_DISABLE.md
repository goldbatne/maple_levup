# 레거시 NPC 비활성화

`roguelite_run_mode_enabled`가 켜진 신규 모드에서 다음 NPC는 보이지 않고 터치 이벤트를 등록하지 않는다.

- RebirthNpc
- GoddessNpc
- HeroNpc
- Bowmaster 시험 NPC(공용 HeroNpc 경로)

잘못 사용되던 `roguelite_mode_enabled` 키는 `roguelite_run_mode_enabled`로 통일했다. 기존 모델과 데이터는 삭제하지 않았다.
