from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[1]
data=[
('이미지 생성 도구','최초: manifest image_gen 자기보고; refinement: built-in image_gen__imagegen 호출 확인','built-in image_gen__imagegen 호출 확인','최초는 호출 미확보, refinement와 같은 도구명','도구명 차이 주원인 주장 불가'),
('모델/모드','최초 UNKNOWN; refinement precise-object-edit라는 프롬프트 분류','new generation / alpha edit; 실제 모델버전 UNKNOWN','모델 ID를 API 파라미터로 지정한 기록 없음','IMAGE_TOOL_OR_MODEL_DIFFERENCE UNKNOWN'),
('MONSTER_IMAGE','최초 manifest 사용 주장/호출 UNKNOWN; refinement 호출 없음','초기/RESTART/ANCHOR1/GRAMMAR 실제입력; ANCHOR2 누락','국소동일원화편집과 새소재제작 차이','ANCHOR2 정체성 참조 누락 확인'),
('VFX reference','최초 UNKNOWN; refinement 기존 마노 대상 및 앞뒤 프레임','마노F04 → blueF04/redF05 → slimeF04 → blueF04','새포자소재와 다른 VFX 정지예시','실제입력 YES지만 동일소재/시간이웃 아님'),
('ICON reference','최초 UNKNOWN; refinement 없음','초기마노ICON으로 새ICON 생성→CAST에 새ICON 투입; 이후없음','초기VFX에 ICON 마감 연결','초기 ICON_REFERENCE_DOMINANCE 가장 유력'),
('reference 수','최초 UNKNOWN; refinement2~3장','초기ICON2/CAST3;RESTART3;ANCHOR2→1;GRAMMAR2','개수와역할이변경됨','개수자체보다역할/내용 차이'),
('reference 우선순위','최초 UNKNOWN; refinement 기존대상 최우선','초기ICON 연결;후기 VFX 중심','완성된동일형상 보존 대상 없음','신규소재번역 검증이 별도로 필요'),
('prompt 구조','최초 UNKNOWN; refinement 경계만변경/중앙보존','WHAT+풍부한마감형용사+추가형태지시+금지어','pointed comma wisps 등 명세외구체화','PROMPT_DRIFT 확인; 영향정도는추론'),
('투명 배경 요청','최초 manifest 투명;refinement 투명실패→검정','투명→검정→투명재시도→blue/magenta','실패에따라방법변경','성공지원여부를요청만으로보장못함'),
('실제 alpha 출력 여부','승인최종49개 RGBA; 최초원시UNKNOWN;refinement rawRGB','최초ICON RGBA;CAST/후기원본RGB','혼합반환','항상RGBA불가능하다는주장은틀림'),
('후처리 방식','최초UNKNOWN;refinement 발광외곽만추정/원래중앙보존','새원화전체 밝기키/채널비율키','적용범위/전경보존 차이','알파손상 직접확인'),
('시트/프레임 생성 방식','최초manifest 시트균등분할;refinement개별수리','초기/RESTART4x2시트;후기단일F03','후기는전체프레임미제작','단일프레임으로리듬PASS불가'),
('검수 시점','원본승인이력;refinement3배경/보존검사후패키징','초기ZIP후거부;후기앵커에서차단','초기파일게이트/아트게이트 혼동','품질미달확산원인;후기차단은정상')]
with (R/'AREA00_VS_AREA01.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['항목','AREA00 성공','AREA01 실패','차이','영향 가능성']);w.writerows(data)
# Preserve relevant existing records byte-for-byte; never execute production scripts.
import shutil
A=Path('D:/maplestory_levup/docs/art');dest=R/'evidence/source_records';dest.mkdir(exist_ok=True)
paths=[A/'area00-images-output/AREA_00_IMAGES_OUTPUT/OUTPUT_MANIFEST.md',A/'area00-images-output/AREA_00_IMAGES_IMPORT_REPORT.md',A/'area00_refinement/20260912_203404/work/refine.py',A/'area00_refinement/20260912_203404/PNG_CHANGE_MAP.csv',A/'area00_refinement/20260912_203404/provenance/image_edits/PROMPTS.md']
for run,sub in [('20260912_212559','work'),('20260912_220728_RESTART','work'),('20260912_222656_ANCHOR','records'),('20260912_225116_GRAMMAR','records')]:
 base=A/'output_style_unified_batches'/run; paths.append(base/'PRODUCTION_STATE.json'); paths.extend(p for p in (base/sub).iterdir() if p.suffix in ['.py','.txt'] and p.is_file())
for i,p in enumerate(paths):shutil.copy2(p,dest/(f'{i:02}_'+p.name))
rows=list(csv.DictReader((R/'REFERENCE_TRACE.csv').open(encoding='utf-8-sig')));bad=[]
for row in rows:
 if row['sha256'] in ['UNKNOWN','MISSING']:continue
 p=Path(row['reference_path']);h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=row['sha256']:bad.append(str(p))
required=['ROOT_CAUSE_SUMMARY.md','AREA00_SUCCESS_PIPELINE.md','AREA01_FAILURE_PIPELINE.md','AREA00_VS_AREA01.csv','REFERENCE_TRACE.csv','TOOL_INPUT_TRACE.md','ALPHA_PIPELINE_ANALYSIS.md','NEXT_PRODUCTION_PLAN.md']
report={'required_files':{n:(R/n).is_file() for n in required},'reference_rows':len(rows),'changed_reference_hashes':bad,'new_generation_calls':0,'art_edits':0,'zip_created':False,'production_resumed':False,'limitations':['AREA00 original generation call unknown','hidden image model unknown','causal dominance cannot be measured from observational logs']}
(R/'evidence/DIAGNOSIS_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
