# 이미지 편집 도구 기록

도구: built-in image_gen.imagegen, precise-object-edit. 생성 전체를 최종 PNG로 교체하지 않고 외곽 마스크 안에서만 채택했다. 원시 결과·마스크·정합본·접합본은 같은 폴더에 보존한다.

## F05 채택 시도

입력: work/BLACK_004_m_mano_s_mon_mano_F05.png (편집 대상), work/BLACK_004_m_mano_s_mon_mano_F06.png (시간 참조). 앞선 시도에서 검수의 F04~F07 보드도 참조했다.

Precise local repair of IMAGE 1 ONLY, animation F05. Image 2 is the following frame reference. Image 1 has an unrelated partial cyan curl at extreme right (x616..640 on original 768x768 canvas) from the neighboring cell. Remove that stray curl, keep the main oval's right tip and softly complete its own faint outer glow. Preserve exact composition, scale, placement, central pearl, petals, upper droplets, original rainbow arc and colors, soft rendering. Only far right boundary may change. Do not re-center, resize, add particles, or redraw intact artwork. Single frame on uniform PURE BLACK RGB (0,0,0) background, no checkerboard, no texture, no text. Soft glow falloff into black. Keep existing 768x768 composition.

## F06 채택 시도

입력: work/BLACK_004_m_mano_s_mon_mano_F06.png (편집 대상), F05와 F07의 BLACK 작업본 (시간 참조).

Precise local repair of IMAGE 1 ONLY (animation F06). Images 2 and 3 are neighboring animation references, do not output them. Keep exact 768x768 composition, same size and placement. Repair the abruptly clipped LEFT end of the low rainbow oval at x128 and RIGHT end at x640; continue existing arcs naturally only a little into the empty margins. Remove the unrelated detached cyan sliver at far right from adjacent cell. Keep all intact central pixels, pearl, petals, upward beam, droplets, stars, curve shapes, palette and soft glow unchanged. Single existing game animation frame. No redesign, no sharper outlines, no added effects or particles, no movement/recentering/resizing. Use absolutely uniform PURE BLACK RGB background (0,0,0), no checkerboard, no texture, no labels. This black-composited edge repair is used to recover luminous edge pixels only, not replace the central source. Keep soft falloff to black.

## F07 채택 시도

입력: work/BLACK_004_m_mano_s_mon_mano_F07.png (편집 대상), F06 BLACK 작업본, 검수 sources/m_mano/004_m_mano_s_mon_mano_F08.png (시간 참조).

Precise local repair of IMAGE 1 ONLY (animation F07). Images 2 and 3 are preceding/following references only. Keep exact 768x768 composition and existing artwork size and placement. Repair the abruptly clipped LEFT turquoise/rainbow edge at x128 by completing the naturally rounded curve just into the empty left margin. Keep original asymmetry. Preserve central pearl, petals, two upper splashes, small pearls, all original arc shapes, color, soft focus and glow. Do not redesign or recenter or sharpen or enlarge or add particles. Output single frame, uniform PURE BLACK RGB background (0,0,0), no checkerboard, no textured background, no text. Soft glow falling into black. Only damaged left boundary should change.

## F05 폐기 시도

편집 대상: 투명 패딩 EDIT_F05, 시간 참조: 검수 m_mano_frames_04_07.png. 실제 투명 RGBA, 같은 팔레트·중앙·형태 유지와 오른쪽 끝 복원/인접셀 조각 제거를 요청했다. 결과가 1254² RGB이며 체크무늬가 배경으로 구워져 있어 납품에서 제외했다.
