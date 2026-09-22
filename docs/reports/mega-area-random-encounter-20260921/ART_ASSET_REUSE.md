# 아트·맵 자산 재사용

- 기존 159개 사냥/보스 맵과 `RoomTable` 연결을 삭제하지 않고 Mega Area의 Room/Chunk 원천으로 재사용했다.
- 몬스터 모델과 AnimationClip, 플레이어 스킬 VFX, 투사체 RUID, 아이콘은 새로 만들거나 교체하지 않았다.
- 혼합 조우는 각 종의 기존 `model_id`를 그대로 스폰한다.
- 최종 보스 20종도 기존 모델·공격·VFX를 그대로 사용한다.
- 새 아트 생성, 이미지 수정, Resource Storage 등록, AnimationClip 변경은 수행하지 않았다.
