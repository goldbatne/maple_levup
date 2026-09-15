from pathlib import Path
import csv
import hashlib
import io
import json
import re
import time
import zipfile

BASE = Path(__file__).parent.parent / "images-input-packages"
COLLECTION = Path(__file__).parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return data.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def roles(data, folder):
    text = decode(data[folder + "/RUNTIME_ROLE_MAP.md"])
    match = re.search(r"required NEW_ART roles:\s*\*\*(.+?)\*\*", text)
    assert match
    return {x.strip() for x in match.group(1).split("|")}


def frame_count(data, folder):
    text = decode(data[folder + "/GENERATION_SPEC.md"])
    return int(re.search(r"^- VFX:\s*(\d+) frames", text, re.M).group(1))


def replace_with_retry(source, target):
    last = None
    for _ in range(12):
        try:
            source.replace(target)
            return
        except PermissionError as error:
            last = error
            time.sleep(0.5)
    raise last


def main():
    packages = sorted(BASE.glob("AREA_*_IMAGES_INPUT.zip"))
    assert len(packages) == 20
    report = {"status": "PASS", "areas": [], "checks": []}
    for zip_path in packages:
        area = zip_path.stem[5:7]
        root = zip_path.stem + "/"
        prompt_path = BASE / f"AREA_{area}_CHATGPT_PRODUCTION_PROMPT.txt"
        prompt = prompt_path.read_bytes()
        with zipfile.ZipFile(zip_path) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            data = {n[len(root):]: archive.read(n) for n in names if n.startswith(root) and not n.endswith("/")}
        rows = list(csv.DictReader(io.StringIO(decode(data["AREA_MANIFEST.csv"]))))
        calculated_vfx = sum(frame_count(data, r["folder"]) for r in rows if "VFX" in roles(data, r["folder"]))
        calculated_icons = sum("ICON" in roles(data, r["folder"]) for r in rows)
        version = json.loads(data["COMMAND_SYSTEM_VERSION.json"])
        assert version["version"] == "single-skill-pipeline-v1"
        assert version["required_vfx_frames"] == calculated_vfx
        assert version["required_icons"] == calculated_icons
        assert data["CHATGPT_IMAGES_MASTER_PROMPT.md"] == prompt
        text = decode(prompt)
        assert "Area 전체 동시 생성 금지" in text
        assert "보고서만 든 ZIP, 이미지 한 장짜리 ZIP을 납품하지 않는다" in text
        assert "TOOL_INTERNAL_REFERENCE_AUDIT=UNAVAILABLE" in text
        assert text.count("## 이 Area의 계산된 필수 수량") == 1
        board_names = [n for n in names if n.endswith("_BOARD.png")]
        manifest_names = [n for n in names if n.endswith("_BOARD_MANIFEST.json")]
        assert len(board_names) == len(rows) * 2
        assert len(manifest_names) == len(rows)
        for name in manifest_names:
            board = json.loads(data[name[len(root):]])
            assert len(board["required_generation_inputs"]) == 3
            for path in board["required_generation_inputs"]:
                assert path in data
            for group in (board["official_vfx_board"], board["area00_finish_board"]):
                assert sha(data[group["path"]]) == group["sha256"]
                for tile in group["tiles"]:
                    assert sha(data[tile["source_path"]]) == tile["source_sha256"]
        hashes = list(csv.DictReader(io.StringIO(decode(data["INPUT_FILE_HASHES.csv"]))))
        for item in hashes:
            assert sha(data[item["path"]]) == item["sha256"]
            assert len(data[item["path"]]) == int(item["bytes"])
        item = {
            "area": area,
            "area_name": rows[0]["area_name"],
            "skills": len(rows),
            "vfx_frames": calculated_vfx,
            "icons": calculated_icons,
            "prepared_boards": len(board_names),
            "zip_bytes": zip_path.stat().st_size,
            "zip_sha256": sha(zip_path.read_bytes()),
            "prompt_sha256": sha(prompt),
            "status": "PASS",
        }
        report["areas"].append(item)
        print("verified", area, calculated_vfx, calculated_icons, len(board_names), flush=True)

    index_path = BASE / "ALL_AREAS_INDEX.csv"
    index = list(csv.DictReader(io.StringIO(index_path.read_text(encoding="utf-8-sig"))))
    assert len(index) == 20
    for row in index:
        item = next(x for x in report["areas"] if x["area"] == row["area_num"].zfill(2))
        row.update(zip_bytes=item["zip_bytes"], zip_sha256=item["zip_sha256"], prompt_sha256=item["prompt_sha256"])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(index[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(index)
    temp = index_path.with_suffix(".csv.new")
    temp.write_bytes(b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8"))
    replace_with_retry(temp, index_path)

    report["total_areas"] = len(report["areas"])
    report["total_skills"] = sum(x["skills"] for x in report["areas"])
    report["total_vfx_frames"] = sum(x["vfx_frames"] for x in report["areas"])
    report["total_icons"] = sum(x["icons"] for x in report["areas"])
    report["total_prepared_boards"] = sum(x["prepared_boards"] for x in report["areas"])
    report["checks"] = [
        "20 ZIP CRC",
        "104 skill role/count calculations from RUNTIME_ROLE_MAP and GENERATION_SPEC",
        "208 prepared boards and all source tile hashes",
        "three concrete reference image inputs per skill",
        "external TXT byte-equals internal master",
        "single computed quantity section and no area-wide generation",
        "all INPUT_FILE_HASHES entries",
        "ALL_AREAS_INDEX hashes",
    ]
    (COLLECTION / "ALL_AREA_COMMAND_SYSTEM_VALIDATION.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # A failed replacement can leave only this suffix. Remove it after all targets passed.
    stale = []
    for path in BASE.glob("AREA_*_IMAGES_INPUT.zip.tmp"):
        resolved = path.resolve()
        assert resolved.parent == BASE.resolve() and resolved.name.endswith(".zip.tmp")
        stale.append(str(path))
        path.unlink()
    report["removed_verified_stale_temp_files"] = stale
    (COLLECTION / "ALL_AREA_COMMAND_SYSTEM_VALIDATION.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({k: report[k] for k in ["status", "total_areas", "total_skills", "total_vfx_frames", "total_icons", "total_prepared_boards", "removed_verified_stale_temp_files"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
