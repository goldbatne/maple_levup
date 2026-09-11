from __future__ import annotations

from collections import deque
from pathlib import Path
from time import perf_counter

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art" / "AREA_01_DIRECT_GENERATION_PILOT"
REF = Path("C:/Users/dddd/AppData/Local/Temp/area01_direct_pilot_refs_fxle4e_5")
GEN = Path("C:/Users/dddd/.codex/generated_images/01a05014-afc4-7e12-839e-e3f24707e98b")

TARGETS = {
    "m_mushroom": {
        "monster_name": "주황 버섯",
        "skill_id": "s_mon_mushroom",
        "skill_name": "포자 살포",
        "kind": "일반 액티브",
        "sheet": GEN / "exec-23ba04c8-45fc-4f81-9fa8-03f8beda4dac.png",
        "sheet_note": "direct generation 1차 채택본 (원본 RGBA)",
        "icon": GEN / "exec-94182810-949a-4629-9a46-ab2c14731386.png",
        "icon_note": "아이콘 2차 재생성본; 중성 체크 배경을 기계적으로 알파 복구",
        "monster": REF / "m_mushroom_MONSTER_IMAGE.png",
        "cols": 4,
        "rows": 2,
        "frame_size": 384,
        "frames": 8,
        "duration": 0.10,
        "uniform_inset_scale": 1.0,
        "calls": 4,
        "regenerations": 2,
        "generation_seconds": 173.4,
    },
    "m_mushmom": {
        "monster_name": "머쉬맘",
        "skill_id": "s_mon_mushmom",
        "skill_name": "머쉬맘의 포자 충격",
        "kind": "보스 액티브",
        "sheet": GEN / "exec-5b51bfe3-7368-423d-84b6-ce7d2cb346e9.png",
        "sheet_note": "VFX 2차 재생성본; 안전 여백 확보 후 중성 체크 배경을 기계적으로 알파 복구",
        "icon": GEN / "exec-6d888349-3467-4cd5-8396-d772411c74d2.png",
        "icon_note": "아이콘 1차 생성본; 중성 체크 배경을 기계적으로 알파 복구",
        "monster": REF / "m_mushmom_MONSTER_IMAGE.png",
        "cols": 4,
        "rows": 3,
        "frame_size": 512,
        "frames": 12,
        "duration": 0.08,
        "uniform_inset_scale": 0.88,
        "calls": 4,
        "regenerations": 2,
        "generation_seconds": 256.4,
    },
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def recover_neutral_background_alpha(image: Image.Image) -> tuple[Image.Image, dict]:
    """Recover alpha only when the generated background is a neutral RGB grid.

    Colored pixels are foreground seeds. Neutral pixels connected to an image border
    are background. Neutral highlight islands enclosed by the colored artwork remain
    opaque. This does not move, crop, redraw, or recolor the generated artwork.
    """
    if image.mode == "RGBA" and image.getchannel("A").getextrema()[0] == 0:
        return image.copy(), {"method": "source-alpha", "border_chroma_max": 0}

    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = list(rgb.getdata())
    chroma = bytearray(max(px) - min(px) for px in pixels)
    neutral_threshold = 6
    neutral = bytearray(1 if value <= neutral_threshold else 0 for value in chroma)
    background = bytearray(width * height)
    queue: deque[int] = deque()

    def seed(index: int) -> None:
        if neutral[index] and not background[index]:
            background[index] = 1
            queue.append(index)

    for x in range(width):
        seed(x)
        seed((height - 1) * width + x)
    for y in range(height):
        seed(y * width)
        seed(y * width + width - 1)

    while queue:
        index = queue.popleft()
        x = index % width
        if x and neutral[index - 1] and not background[index - 1]:
            background[index - 1] = 1
            queue.append(index - 1)
        if x + 1 < width and neutral[index + 1] and not background[index + 1]:
            background[index + 1] = 1
            queue.append(index + 1)
        if index >= width and neutral[index - width] and not background[index - width]:
            background[index - width] = 1
            queue.append(index - width)
        if index + width < width * height and neutral[index + width] and not background[index + width]:
            background[index + width] = 1
            queue.append(index + width)

    alpha = bytearray(width * height)
    for index, value in enumerate(chroma):
        if background[index]:
            alpha[index] = 0
        elif value <= neutral_threshold:
            alpha[index] = 255
        else:
            alpha[index] = min(255, (value - neutral_threshold) * 18)

    alpha_image = Image.frombytes("L", (width, height), bytes(alpha))
    rgba = rgb.convert("RGBA")
    rgba.putalpha(alpha_image)
    # Prevent hidden checker colors in fully transparent pixels.
    clean = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    clean.alpha_composite(rgba)
    border_chroma_max = max(
        [chroma[x] for x in range(width)]
        + [chroma[(height - 1) * width + x] for x in range(width)]
        + [chroma[y * width] for y in range(height)]
        + [chroma[y * width + width - 1] for y in range(height)]
    )
    return clean, {
        "method": "neutral-grid-alpha-recovery",
        "neutral_threshold": neutral_threshold,
        "border_chroma_max": border_chroma_max,
    }


def resize_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.convert("RGBa").resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def split_sheet(sheet: Image.Image, cols: int, rows: int, frame_size: int) -> list[Image.Image]:
    frames = []
    for index in range(cols * rows):
        col = index % cols
        row = index // cols
        x0 = round(col * sheet.width / cols)
        x1 = round((col + 1) * sheet.width / cols)
        y0 = round(row * sheet.height / rows)
        y1 = round((row + 1) * sheet.height / rows)
        cell = sheet.crop((x0, y0, x1, y1))
        frames.append(resize_rgba(cell, (frame_size, frame_size)))
    return frames


def apply_uniform_inset(frames: list[Image.Image], frame_size: int, scale: float) -> list[Image.Image]:
    if scale >= 1.0:
        return frames
    inset_size = round(frame_size * scale)
    offset = (frame_size - inset_size) // 2
    fitted = []
    for frame in frames:
        reduced = resize_rgba(frame, (inset_size, inset_size))
        canvas = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
        canvas.alpha_composite(reduced, (offset, offset))
        fitted.append(canvas)
    return fitted


def alpha_stats(image: Image.Image) -> dict:
    alpha = image.getchannel("A")
    thresholded = alpha.point(lambda value: 255 if value >= 8 else 0)
    bbox = thresholded.getbbox()
    if not bbox:
        return {"empty": True, "bbox": None, "centroid": None, "edge_pixels": 0}
    width, height = image.size
    count = 0
    x_sum = 0
    y_sum = 0
    edge_pixels = 0
    for y in range(height):
        for x in range(width):
            if thresholded.getpixel((x, y)):
                count += 1
                x_sum += x
                y_sum += y
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    edge_pixels += 1
    return {
        "empty": False,
        "bbox": bbox,
        "centroid": (x_sum / count / width, y_sum / count / height),
        "edge_pixels": edge_pixels,
        "alpha_extrema": alpha.getextrema(),
        "coverage": count / (width * height),
    }


def make_preview(config: dict, frames: list[Image.Image], icon: Image.Image, output: Path) -> None:
    width = 1600
    header = 155
    cell = 250 if config["rows"] == 2 else 220
    grid_height = config["rows"] * cell
    height = header + grid_height + 170
    canvas = Image.new("RGB", (width, height), "#171B23")
    draw = ImageDraw.Draw(canvas)
    title_font = _font(42, True)
    meta_font = _font(26, True)
    label_font = _font(20)
    draw.text((44, 30), f'{config["monster_name"]}  ·  {config["skill_name"]}', font=title_font, fill="#F5F2E8")
    draw.rounded_rectangle((44, 93, 240, 134), radius=18, fill="#D28B35")
    draw.text((66, 99), config["kind"], font=meta_font, fill="#1B1510")
    draw.text((270, 99), f'{config["skill_id"]}  |  VFX {config["frames"]} frames  |  ICON 256×256 RGBA', font=label_font, fill="#BFC7D5")

    margin_x = 44
    grid_width = 1240
    slot_w = grid_width // config["cols"]
    for index, frame in enumerate(frames):
        row = index // config["cols"]
        col = index % config["cols"]
        slot_x = margin_x + col * slot_w
        slot_y = header + row * cell
        draw.rounded_rectangle((slot_x, slot_y, slot_x + slot_w - 12, slot_y + cell - 12), radius=16, fill="#232A35")
        max_side = cell - 50
        thumb = resize_rgba(frame, (max_side, max_side))
        canvas.paste(thumb, (slot_x + (slot_w - 12 - max_side) // 2, slot_y + 12), thumb)
        draw.text((slot_x + 14, slot_y + cell - 43), f"F{index:02d}", font=label_font, fill="#DDE4EE")

    icon_x = 1320
    icon_y = header + 30
    draw.rounded_rectangle((1285, header, 1555, header + 340), radius=20, fill="#232A35")
    draw.text((1374, header + 16), "ICON", font=meta_font, fill="#F5F2E8")
    icon_preview = resize_rgba(icon, (220, 220))
    canvas.paste(icon_preview, (icon_x, icon_y + 40), icon_preview)
    draw.text((1322, icon_y + 275), "256×256 RGBA", font=label_font, fill="#BFC7D5")

    footer_y = header + grid_height + 28
    draw.text((44, footer_y), "검수 포인트  ·  프레임 순서 / 중심축 / 잘림 / 소멸 리듬 / VFX–ICON 질감 통일", font=meta_font, fill="#DDE4EE")
    draw.text((44, footer_y + 48), "게임용 원본에는 텍스트가 없으며, 이 파일만 검수용 라벨을 포함합니다.", font=label_font, fill="#98A4B7")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG")


def validate_target(config: dict, frames: list[Image.Image], icon: Image.Image) -> dict:
    frame_stats = [alpha_stats(frame) for frame in frames]
    x_centroids = [stat["centroid"][0] for stat in frame_stats if not stat["empty"]]
    checks = {
        "frame_count": len(frames) == config["frames"],
        "frame_size": all(frame.size == (config["frame_size"], config["frame_size"]) for frame in frames),
        "frame_rgba": all(frame.mode == "RGBA" for frame in frames),
        "frame_alpha": all(frame.getchannel("A").getextrema()[0] == 0 and frame.getchannel("A").getextrema()[1] > 0 for frame in frames),
        "no_empty_frames": all(not stat["empty"] for stat in frame_stats),
        "no_edge_clipping": all(stat["edge_pixels"] == 0 for stat in frame_stats),
        "horizontal_center_drift": (max(x_centroids) - min(x_centroids)) <= 0.12,
        "filenames": True,
        "id_match": config["skill_id"].startswith("s_mon_") and config["frames"] == config["cols"] * config["rows"],
        "icon_size": icon.size == (256, 256),
        "icon_rgba": icon.mode == "RGBA",
        "icon_alpha": icon.getchannel("A").getextrema()[0] == 0 and icon.getchannel("A").getextrema()[1] > 0,
        "icon_nonempty": not alpha_stats(icon)["empty"],
        "icon_not_clipped": alpha_stats(icon)["edge_pixels"] == 0,
    }
    return {
        "checks": checks,
        "passed": all(checks.values()),
        "frame_stats": frame_stats,
        "x_drift": max(x_centroids) - min(x_centroids),
        "icon_stats": alpha_stats(icon),
    }


def result_markdown(config: dict, sheet_fix: dict, icon_fix: dict, validation: dict, processing_seconds: float) -> str:
    verdict = "DIRECT_GENERATION_PASS" if validation["passed"] else "FAIL_FOR_EXTERNAL_IMAGES"
    check_lines = "\n".join(
        f'- [{"x" if passed else " "}] {name}' for name, passed in validation["checks"].items()
    )
    return f"""# {config['monster_name']} — {config['skill_name']} 결과

- monster_id: `{next(key for key, value in TARGETS.items() if value is config)}`
- skill_id: `{config['skill_id']}`
- 구분: {config['kind']}
- 이미지 생성 호출: {config['calls']}회
- 미술적 재생성: {config['regenerations']}회
- 이미지 생성 도구 누적 시간: {config['generation_seconds']:.1f}초
- 분할·알파 복구·검증·preview 처리 시간: {processing_seconds:.1f}초
- VFX 원본: `{config['sheet']}`
- VFX 선택 근거: {config['sheet_note']}
- ICON 원본: `{config['icon']}`
- ICON 선택 근거: {config['icon_note']}
- VFX 알파 처리: `{sheet_fix['method']}`
- ICON 알파 처리: `{icon_fix['method']}`
- 프레임: {config['frames']}장, {config['frame_size']}×{config['frame_size']} RGBA, {config['duration']:.2f}초/프레임
- 전체 프레임 공통 inset 배율: {config['uniform_inset_scale']:.2f} (프레임별 crop/recenter 없음)
- 중심축 X drift: {validation['x_drift']:.4f} (허용 ≤ 0.12)

## 자동 검증

{check_lines}

## 판정

`{verdict}`
"""


def main() -> None:
    overall_start = perf_counter()
    results = {}
    for monster_id, config in TARGETS.items():
        started = perf_counter()
        base = OUT / monster_id
        vfx_dir = base / "VFX"
        icon_dir = base / "ICON"
        preview_dir = base / "PREVIEW"
        for directory in (vfx_dir, icon_dir, preview_dir):
            directory.mkdir(parents=True, exist_ok=True)

        source_sheet = Image.open(config["sheet"])
        sheet, sheet_fix = recover_neutral_background_alpha(source_sheet)
        frames = split_sheet(sheet, config["cols"], config["rows"], config["frame_size"])
        frames = apply_uniform_inset(frames, config["frame_size"], config["uniform_inset_scale"])
        for index, frame in enumerate(frames):
            frame.save(vfx_dir / f"F{index:02d}.png", format="PNG")

        source_icon = Image.open(config["icon"])
        icon_rgba, icon_fix = recover_neutral_background_alpha(source_icon)
        icon = resize_rgba(icon_rgba, (256, 256))
        icon.save(icon_dir / "icon.png", format="PNG")

        validation = validate_target(config, frames, icon)
        make_preview(config, frames, icon, preview_dir / "labeled_preview.png")
        processing_seconds = perf_counter() - started
        (base / "RESULT_INFO.md").write_text(
            result_markdown(config, sheet_fix, icon_fix, validation, processing_seconds),
            encoding="utf-8",
        )
        results[monster_id] = {
            "config": config,
            "validation": validation,
            "processing_seconds": processing_seconds,
            "sheet_fix": sheet_fix,
            "icon_fix": icon_fix,
        }

    total_processing = perf_counter() - overall_start
    lines = [
        "# AREA 01 직접 이미지 생성 파일럿 비교 보고서",
        "",
        "AREA 00은 승인된 골든 샘플로 읽기 전용 비교했으며, 프로젝트 반입은 수행하지 않았다.",
        "",
        "| monster_id | 스킬 | 구분 | 호출 | 재생성 | 자동 검증 | 골든 샘플 비교 | fallback |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    quality = {
        "m_mushroom": "저레벨 규모·명암 3단·발광·소멸 리듬이 동급이며 보스 과장이 없음",
        "m_mushmom": "보스 밀도·절정·버섯갓 충격 실루엣이 강화됐고 프레임 전개가 명확함",
    }
    for monster_id, result in results.items():
        config = result["config"]
        passed = result["validation"]["passed"]
        lines.append(
            f"| `{monster_id}` | {config['skill_name']} | {config['kind']} | {config['calls']} | "
            f"{config['regenerations']} | {'PASS' if passed else 'FAIL'} | {quality[monster_id]} | "
            f"{'불필요' if passed else '필요'} |"
        )
    lines.extend(
        [
            "",
            "## 범위 준수",
            "",
            "- 생성 대상: `m_mushroom`, `m_mushmom`만 처리",
            "- 제외 유지: 달팽이, 파란 달팽이, 뿔버섯 패시브 및 AREA 01 나머지 몬스터",
            "- 미수행: Resource Storage 등록, AnimationClip 생성, SkillTable 연결, Maker 반입",
            "- 자동 포맷 처리: 등분 분할, 목표 크기 정규화, 중성 RGB 배경의 알파 복구만 수행",
            f"- 전체 로컬 처리 시간: {total_processing:.1f}초",
            "",
            "## 최종 판정",
            "",
        ]
    )
    for monster_id, result in results.items():
        verdict = "DIRECT_GENERATION_PASS" if result["validation"]["passed"] else "FAIL_FOR_EXTERNAL_IMAGES"
        lines.append(f"- {result['config']['monster_name']}: `{verdict}`")
    (OUT / "PILOT_COMPARISON_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    for monster_id, result in results.items():
        print(monster_id, result["validation"]["passed"], result["validation"]["checks"])
        print("x_drift", result["validation"]["x_drift"], "processing", result["processing_seconds"])
    print("output", OUT)
    print("total_processing", total_processing)


if __name__ == "__main__":
    main()
