# PROJECTILE SCOPE REVIEW — V2.3

All 12 actual monster projectile visual roles are NEW_ART. Engine movement is unchanged; existing projectile RUIDs remain evidence only until approved import.

| Area | monster | skill | current RUID | new files | timing | targeting | impact | future target |
|---|---|---|---|---|---|---|---|---|
| area_02 | `m_stumpy` | `s_mon_stumpy` | `c6b3f052e977479ea5ad5329ce0981ca` | `PROJECTILE/008_m_stumpy_s_mon_stumpy_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 5 | 0.8 after 0.35s | `projectile_ruid` |
| area_03 | `m_faust` | `s_mon_faust` | `49b21aaa1d574ba787149841a31bf1a5` | `PROJECTILE/005_m_faust_s_mon_faust_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 4 | 0.8 after 0.35s | `projectile_ruid` |
| area_08 | `m_star_pixie` | `s_mon_star_pixie` | `b61e7e2a50b2405794f88fdddf44b73a` | `PROJECTILE/001_m_star_pixie_s_mon_star_pixie_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6 | 0.8 after 0.35s | `projectile_ruid` |
| area_08 | `m_lunar_pixie` | `s_mon_lunar_pixie` | `4f6509d9539f4d76a9bb4e8f17e12cc7` | `PROJECTILE/003_m_lunar_pixie_s_mon_lunar_pixie_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6.4 | 0.8 after 0.35s | `projectile_ruid` |
| area_10 | `m_shark` | `s_mon_shark` | `209c4567073b424e8d445cea7efb80e3` | `PROJECTILE/004_m_shark_s_mon_shark_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6.5 | 0.8 after 0.35s | `projectile_ruid` |
| area_11 | `m_king_bloctopus` | `s_mon_king_bloctopus` | `a2da67e687994755a8943c2bcf871902` | `PROJECTILE/004_m_king_bloctopus_s_mon_king_bloctopus_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6.8 | 0.8 after 0.35s | `projectile_ruid` |
| area_14 | `m_roid` | `s_mon_roid` | `e51545cbf94349f59f4431e2e76d2cdc` | `PROJECTILE/004_m_roid_s_mon_roid_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 7 | 0.8 after 0.35s | `projectile_ruid` |
| area_14 | `m_chimera` | `s_mon_chimera` | `ab113d9a5ca5402d85ecc2ab7a4f51a1` | `PROJECTILE/005_m_chimera_s_mon_chimera_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6.8 | 0.8 after 0.35s | `projectile_ruid` |
| area_15 | `m_peach_monkey` | `s_mon_peach_monkey` | `9ca14ee512b1489cbb54b2b9833388cd` | `PROJECTILE/003_m_peach_monkey_s_mon_peach_monkey_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 7 | 0.8 after 0.35s | `projectile_ruid` |
| area_15 | `m_tae_roon` | `s_mon_tae_roon` | `5328a3875a32437784c949579f259a00` | `PROJECTILE/005_m_tae_roon_s_mon_tae_roon_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 6.6 | 0.8 after 0.35s | `projectile_ruid` |
| area_17 | `m_dodo` | `s_mon_dodo` | `72e16f10f6ec4cf0a1fe3146e73f0856` | `PROJECTILE/005_m_dodo_s_mon_dodo_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 7 | 0.8 after 0.35s | `projectile_ruid` |
| area_18 | `m_mateon` | `s_mon_mateon` | `22db356cc60940089b7f5d592c7d5813` | `PROJECTILE/001_m_mateon_s_mon_mateon_PROJECTILE_F00.png..._PROJECTILE_F03.png` | 4×0.08=0.32s / non-loop complete playback within 0.35s entity lifetime | 7.4 | 0.8 after 0.35s | `projectile_ruid` |

- Stumpy has no CAST and remains PROJECTILE+ICON only.
- The other 11 keep their CAST requirement and add an independent PROJECTILE requirement.
- No HIT role is added because ResolveThrowHit has no visual asset field or effect spawn call.
