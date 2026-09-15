# MSW 공식 스킬 디자인 참고 라이브러리

수집 범위: 공개 API가 skill 카테고리로 반환한 **5,299개 팩** 및 팩에 연결된 **53,998개 시각 리소스 표시용 PNG/GIF**. API에 노출되지 않은 자료까지 전부 확보했다고 주장하지 않는다. 스킬 팩의 음향 4,264개는 디자인 목적에 맞게 목록만 보존한다.

VIEWER.html을 열어 이름/팩 ID로 검색하면 각 팩의 로컬 PNG/GIF를 볼 수 있다. CATALOG.json에는 역할 경로와 RUID가 연결된다. media에는 CDN 제공 파일을 수정 없이 저장했다. details에는 API 응답을 보존한다. FILE_HASHES.csv에 SHA-256/출처 URL/수집 상태가 있다.

이것은 엔진 원본 전체 덤프가 아니다. GIF 프리뷰에는 배경이나 GIF 팔레트 제한이 있을 수 있고, 프레임 원본 RUID는 메타데이터에만 남아 있을 수 있다. 실제 원본 알파를 복구했다고 주장하지 않는다. 모든 스킬의 최신성/라이브 리비전은 NOT_VERIFIED이며 오래된 스킬과 이벤트·이동 리소스도 함께 들어 있다.

제작 시에는 모든 스킬을 섞지 말고 Area INPUT의 reference_resource_design에서 소재/역할에 맞는 자료를 우선 사용한다. 공식 스킬 디자인의 명암·재질·코어·발광·파편·프레임 전개·ICON 표현을 관찰하고, INPUT의 몬스터 소재와 동작으로 새롭게 만든다. 참고 파일 자체를 새 OUTPUT으로 납품하지 않는다.

수집 상태: PARTIAL. 누락 3개. 세부 상태는 COLLECTION_REPORT.json.


전체 원본 수집 ZIP은 약 3.22GB의 로컬 재생성 가능 산출물이라 Git에 커밋하지 않는다. 당시 ZIP의 SHA-256과 CRC 결과는 `COLLECTION_REPORT.json`에 보존한다. 현재 제작에 필요한 선택 레퍼런스는 각 Area INPUT에 포함돼 있으며, 전체 자료가 다시 필요하면 `CATALOG.json`, `FILE_HASHES.csv`, `downloads.jsonl`과 수집 스크립트로 로컬 ZIP을 재구성한다.
