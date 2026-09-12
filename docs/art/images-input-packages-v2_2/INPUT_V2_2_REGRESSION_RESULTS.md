# INPUT V2.2 validator regression results

- overall: **PASS**
- 모든 오류 주입은 임시 복사본에서만 수행했으며 납품 ZIP은 수정하지 않았다.

| case | expected | actual | test | representative detection |
|---|---|---|---|---|
| positive_unmodified_area02 | PASS | PASS | PASS | none |
| negative_stumpy_cast_role_conflict | FAIL | FAIL | PASS | s_mon_stumpy: required_roles differs across manifest/spec/role map |
| negative_old_exclude_classification | FAIL | FAIL | PASS | style 7: current style_priority differs index=EXCLUDE_STYLE info=UNKNOWN |
