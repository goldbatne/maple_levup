# AREA01 실패 실행 복원

공통 WHAT: AREA_01_IMAGES_INPUT_V2_4.zip, SHA256 7e33f787d2ab9cb1b5b47e41a11431c498eb2e35a18bce49b5c2a483f1c4fa1b. 주황 버섯 m_mushroom / s_mon_mushroom / 포자 살포 / 액티브 / CAST8×384²/.10s 및 ICON256². SOURCE_PROVENANCE의 MONSTER_IMAGE SHA256 0e795f604587cf4f6a4ff0637e518469c8ef35473bcb21ae257d723fe3f8dc89.

## 최초 20260912_212559
- L506 ICON: 실제 MONSTER_IMAGE + AREA00 마노ICON. RGBA1254² 출력.
- L522 CAST: MONSTER_IMAGE + AREA00 마노VFX F04 + 방금 생성한 주황 버섯ICON. 'same professional finish as icon' 지시. RGB1774×887의4×2시트가 반환됨. 원본부터 굵은 금색 경계·광택 연두 물방울·꽃 같은 덩어리. 알파 처리 전 이미 스타일 차이 존재.
- produce.py: 직접RGBA면 유지. RGB이면 검정 경계검사, 외부연결 maxRGB<32부분에 alpha=(maxRGB-3)/29, 나머지불투명, 역합성, 균등분할/resize. 원본source_00_1/2는 ICON끼리/CAST끼리 각각 같은해시: ingest 재시도로 생긴 중복 저장이지 독립 생성2안이 아님.
- 최초 배치는 아트승인 이전 AREA01 ZIP까지 제작됐고 이후 사용자 거부로 철회/격리. 파일 검사와 아트게이트가 분리되지 않은 생산 실패.
- jobs.py는 AREA02 이후 모든 역할에 AREA00 마노ICON을 고정 참조. 이는 현재Area OUTPUT 우선 selector가 아니다. 뿔버섯REFERENCE에서도 마노ICON을 직접사용(L678). 주황 버섯의 VFX참조 자체가 없었다는 결론은 틀림.

## RESTART 20260912_220728_RESTART
L1124/1134/1153: 세 호출 모두 실제 MONSTER_IMAGE + AREA00 blue F04 + red F05. 기존AREA01 OUTPUT/실패본/ICON/Preview/외부STYLE 입력 없음. 첫RGB체커시트 탈락, 이후검정RGB시트. check_mushroom.py의 /126과 check_mushroom3.py의 /253 알파 전경전체추정. 얇아진재질·흐린가장자리/원화덩어리 형태가 불합격. ICON/ZIP 미생성.

## ANCHOR 20260912_222656_ANCHOR
- L1254: AREA00 slimeF04 + 실제MONSTER_IMAGE. 단일절정원본, RGB체커출력.
- L1269: AREA00 slimeF04 **1장만**. MONSTER_IMAGE 없음. 'pointed comma-like powder wisps'로 모티브를 바꾼 지시와 세갈래 장식형출력. AREA00 VFX 전달은 실제 존재.
- L1286: 바로앞 실패원본을 background-extraction 편집 대상으로 사용. 이는 '실패본을 이미지 도구에 전혀 넣지 않았다'는 넓은 표현과 다르지만 스타일positive참조를 사용한 새아트생성은 아님. 편집도RGB체커출력, 채택없음.
- 전체프레임·ICON·ZIP없음. nativealpha 불가를 도구 전체능력으로 일반화할 수 없음: 최초ICON의 실제RGBA 사례 존재.

## GRAMMAR 20260912_225116_GRAMMAR — 가장 최근 앵커 실행
L1373/L1396: AREA00 blueF04 + 실제MONSTER_IMAGE. 기존OUTPUT/실패본/ICON/비교Preview입력 없음. blue matte1254²와magenta matte1536×1024 신규원본2개. 단색배경 Python 분리는 당시 새 사용자 지시가 허용했음.

matte.py: alpha=1-B+.65min(R,G), matte_second.py: alpha=1-B+.68G, 각각순수blue/magenta가정 후역합성. 색가정이 밝은원화까지 적용돼 손상. 두번째는색얼룩뿐 아니라배경값변동으로직사각형 잔류.384²시험2개만 생성, 역할완료0. 스타일/알파실패로보류. 새로운 별도 '가장 최근 실행'은 이GRAMMAR이며 중복계수하지 않는다.

## 기존OUTPUT·Preview 오염 결론
초기새ICON→초기CAST연결은YES. 재시작 이후주황버섯새원화에기존AREA01OUTPUT가자동재선택된것은NO_EVIDENCE. 마노임시ICON경로호출은초기머쉬맘별도사례. AREA00 refinement 첫시도는검수보드를시간참조로사용했지만주황버섯생성의스타일참조에Preview를넣은호출은발견안됨. 파일이폴더에남아있다는것만으로오염판정하지않는다.
