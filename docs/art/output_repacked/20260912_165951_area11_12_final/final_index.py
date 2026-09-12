from package_final import *
def main():
    index=[];pres=[]
    for s in rows(BASE/'AREA_SELECTION.csv'):
        a=s['area_id'];new=RUN/f'AREA_{a[-2:]}_IMAGES_OUTPUT_V2_4_FINAL_CANDIDATE.zip'
        if a in ['area_11','area_12'] and new.exists():
            path=new;status='PACKAGED_AND_REEXTRACTED';basis='New limited-scope package; '+('4 PROJECTILE PNGs edited' if a=='area_11' else 'all role PNG bytes preserved');pres.extend(rows(RUN/f'{a}_PNG_CHANGES.csv'))
        else:
            path=Path(s['output_path']);assert sha(path)==s['output_sha256'];status='BLOCKED_ALPHA_NO_CORRECTED_PACKAGE' if a=='area_11' else 'EXISTING_REPACK_REUSED_UNCHANGED';basis='Selected prior original only; NOT final corrected candidate' if a=='area_11' else 'Latest origin-art audit + exact archive SHA256 reused'
        index.append({'area_id':a,'candidate_zip_path':str(path),'sha256':sha(path),'status':status,'basis':basis,'input_v24_path':s['input_path'],'input_v24_sha256':s['input_sha256'],'user_art_approval':'PENDING','runtime_validation':'NOT_RUN'})
    csvwrite(RUN/'CANDIDATE_ZIP_INDEX.csv',index)
    if pres:csvwrite(RUN/'PNG_BYTE_PRESERVATION.csv',pres)
    evidence=[]
    for s in rows(BASE/'AREA_SELECTION.csv'):
        for kind,k,h in [('INPUT','input_path','input_sha256'),('ORIGINAL_SELECTED_OUTPUT','output_path','output_sha256')]:
            evidence.append({'kind':kind,'area_id':s['area_id'],'path':s[k],'expected_sha256':s[h],'actual_sha256':sha(s[k]),'unchanged':sha(s[k])==s[h]})
    csvwrite(RUN/'PROTECTED_ARCHIVE_HASH_CHECK.csv',evidence)
    print('INDEX',len(index),'BLOCKED',sum(r['status'].startswith('BLOCKED') for r in index),'PRESERVE_ROWS',len(pres))
if __name__=='__main__':main()
