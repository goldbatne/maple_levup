# ChatGPT Work Local 배치 실행 인덱스

각 파일은 **한 개의 ChatGPT Work Local 채팅**에서 해당 숫자 구간의 Area들을 독립 작업선으로 함께 제작하는 실행 프롬프트다. 네 배치를 서로 다른 채팅에서 실행한다.

| 배치 | 실행 프롬프트 | 실제 Area | 예상 산출 |
|---|---|---|---|
| 01~05 | `AREA_01_05_CHATGPT_WORK_LOCAL_PARALLEL_PROMPT.txt` | AREA 01~05 | 28스킬, VFX 188, ICON 28, ZIP 5개 |
| 06~10 | `AREA_06_10_CHATGPT_WORK_LOCAL_PARALLEL_PROMPT.txt` | AREA 07~10; AREA 06 제외 | 21스킬, VFX 120, ICON 21, ZIP 4개 |
| 11~15 | `AREA_11_15_CHATGPT_WORK_LOCAL_PARALLEL_PROMPT.txt` | AREA 11~15 | 25스킬, VFX 140, ICON 25, ZIP 5개 |
| 16~20 | `AREA_16_20_CHATGPT_WORK_LOCAL_PARALLEL_PROMPT.txt` | AREA 16~20 | 25스킬, VFX 140, ICON 25, ZIP 5개 |

각 새 Work Local 채팅에는 대상 프롬프트 파일 하나를 지정하고 다음처럼 요청한다.

> 이 프로젝트에서 지정한 배치 프롬프트를 읽고 해당 Area들의 제작을 한 채팅에서 실제 실행해줘.

각 프롬프트는 자신의 구간이 끝난 뒤 다음 구간을 자동 시작하지 않는다.
