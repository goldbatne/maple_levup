from review_audit import *
from collections import Counter
def main():
    rs=json.loads((RUN/'records.json').read_text('utf8'));src=readcsv(RUN/'SOURCE_CHECK.csv');art=readcsv(RUN/'ART_REVIEW.csv');acts=readcsv(RUN/'ACTION_ITEMS.csv');checks=[]
    def check(name,ok,detail=''):
        checks.append({'check':name,'result':'PASS' if ok else 'FAIL','detail':str(detail)})
        assert ok,(name,detail)
    check('source coverage',len(src)==99 and len({r['monster_id'] for r in src})==99)
    check('role coverage',len(art)==209 and len({(r['monster_id'],r['role']) for r in art})==209)
    check('all direct-source evidence',all(r['source_level']=='MSW_ORIGINAL_CONFIRMED' and Path(r['source_copy_path']).exists() and Path(r['resource_query_evidence']).exists() for r in src))
    check('observed role file count',sum(int(r['observed_frame_count']) for r in art)==933)
    check('only one mismatch',[(r['monster_id'],r['role']) for r in art if r['art_judgment']!='NO_OBVIOUS_ISSUE']==[('m_king_bloctopus','PROJECTILE')])
    check('all statuses and approvals',all(r['user_approved']=='NO' and r['style_judgment']=='NO_OBVIOUS_ISSUE' for r in art))
    check('visual boards exist',all(Path(r['visual_evidence'].split('|')[0]).exists() for r in art))
    check('required files',all((RUN/n).exists() and (RUN/n).stat().st_size>0 for n in ['REVIEW_SUMMARY.md','SOURCE_CHECK.csv','ART_REVIEW.csv','ACTION_ITEMS.csv']))
    # End-of-run preservation verification uses only hashes; it does not repeat CRC/PNG-format auditing.
    for r in readcsv(RUN/'AREA_SELECTION.csv'):
        check('INPUT unchanged '+r['area_id'],sha(r['input_path'])==r['input_sha256'])
        check('OUTPUT unchanged '+r['area_id'],sha(r['output_path'])==r['output_sha256'])
    check('models unchanged',all(sha(r['model_path'])==r['model_sha256'] for r in rs))
    check('all read-only evidence unchanged',all(sha(r['path'])==r['sha256'] for r in readcsv(RUN/'EVIDENCE_INDEX.csv')))
    check('source copies hash valid',all(sha(r['source_copy_path'])==r['source_copy_sha256'] for r in src))
    check('repack preservation reuse',len(readcsv(RUN/'REUSE_PNG_CHECK.csv'))==839 and all(r['match']=='True' for r in readcsv(RUN/'REUSE_PNG_CHECK.csv')))
    check('current-approved skill data unchanged',all(r['candidate_vs_approved']=='MATCH' and r['area_match']=='True' for r in readcsv(RUN/'PROJECT_DATA_CHECK.csv')))
    writecsv('REPORT_VALIDATION.csv',checks)
    print('VALIDATION',len(checks),'PASS; source=99 roles=209 files=933 mismatch roles=1; models/archives/evidence unchanged')
if __name__=='__main__':main()
