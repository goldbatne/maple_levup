# Maker 엔트리 저장 실패 정리 기록

## 확인 결과

- Maker 팝업: `엔트리 저장에 실패했습니다. 콘솔에서 내용을 확인하십시오.`
- Build 콘솔 오류: 0건
- Runtime 콘솔 오류: 0건
- PlayerDB 저장 로그: 정상 완료
- 워크스페이스 파일 감사: 보고서/백업 폴더에 원본과 같은 EntryKey를 가진
  `.map`, `.ui`, `.mlua`, `.model`, `.codeblock`, `.userdataset`, `.directory`
  파일이 중복 보관되어 있었음

이 파일들은 Maker가 프로젝트 엔트리로 스캔할 수 있으므로 `Mislocated Entries`와
엔트리 저장 충돌의 원인이 된다.

재실행 후 추가 검증에서 더 근본적인 상태도 확인했다. 실제 최신 작업 파일
243개가 `RootDesk/MyDesk`가 아니라 `Mislocated/MyDesk`에 놓여 있었고,
`RootDesk/MyDesk`는 비어 있었다. 따라서 단순 중복 제거만으로는 충분하지 않았고,
Maker가 읽던 최신 파일을 올바른 RootDesk 위치로 되돌려야 했다.

## 처리

원본 바이트와 상대 경로, SHA-256을 먼저 기록하고 다음 6개 ZIP으로 보존한 뒤,
프로젝트가 스캔하는 위치의 네이티브 확장자 복사본만 제거했다.

- `Mislocated.zip`
- `roguelite-mislocated-backup.zip`
- `roguelite-preinstance-maps.zip`
- `roguelite-premerge.zip`
- `skill-audit-173637-untracked.zip`
- `skill-audit-174133-untracked.zip`

세부 파일별 정보는 `ENTRY_SNAPSHOT_MANIFEST.json`, ZIP 해시는
`ARCHIVE_SHA256.json`을 기준으로 한다. ZIP은 Maker 엔트리로 등록되지 않으므로
프로젝트 내부에 보관해도 안전하다.

## 복원 방법

필요한 파일만 ZIP에서 프로젝트 외부 임시 폴더로 푼 뒤 manifest의 원래 상대
경로를 확인한다. 검토 없이 프로젝트 루트 아래에 ZIP 전체를 다시 풀면 동일한
중복 엔트리 문제가 재발할 수 있다.

## 재발 방지

- 맵 백업 스크립트는 `.map.snapshot` 확장자를 사용한다.
- 스킬 감사 baseline 스크립트는 MSW 네이티브 파일에 `.snapshot`을 덧붙이고
  원래 복원 경로를 metadata에 기록한다.
- Maker가 이미 중복 엔트리를 메모리에 올린 세션에서는 소스 정리 후 한 번
  종료/재실행해야 `Mislocated Entries` 캐시가 비워진다.

## 정리 후 정적 재검사

- `Mislocated/MyDesk` 최신 파일 243개를 별도 ZIP으로 추가 보존
- 최신 작업 파일 전체를 `RootDesk/MyDesk`로 이동
- 초기 보존 ZIP에서 누락된 표·모델·타일셋 25개를 해시 검증 후 보충
- 검사한 MSW 네이티브 파일: 447개
- 확인한 EntryKey: 392개
- 중복 EntryKey: 0개
- `Mislocated` 아래 잔존 네이티브 엔트리 파일: 0개

새 Maker 세션에서 Workspace Refresh와 Save를 실행했고 엔트리 저장 실패 팝업은
재발하지 않았다. Play에서도 SkillTable, MonsterTable 등 데이터셋이 다시
로드됐다. 이후 표시되는 M2A 시각 리소스 검증 오류는 엔트리 저장 실패와 별개의
콘텐츠 검증 항목이다.
