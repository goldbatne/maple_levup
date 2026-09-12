# V2.3 validator regression results

- overall: **PASS**

| Case | Expected | Actual | Test |
|---|---|---|---|
| positive_unmodified_area02 | PASS | PASS | PASS |
| reject_projectile_keep | FAIL | FAIL | PASS |
| reject_invented_stumpy_cast | FAIL | FAIL | PASS |
| reject_invented_hit_role | FAIL | FAIL | PASS |
| reject_projectile_lifetime_overrun | FAIL | FAIL | PASS |

The negative cases run on in-memory copies only; delivery ZIPs are not modified.
