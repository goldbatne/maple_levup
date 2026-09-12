#!/usr/bin/env python3
"""Apply the reproducible V2.3 document-name normalization to built archives."""

from __future__ import annotations

import os
import zipfile
from pathlib import Path


BASE = Path(__file__).resolve().parents[1] / "art" / "images-input-packages-v2_3"


def normalize(path: Path) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as dst:
        for info in src.infolist():
            name = info.filename.replace("\\", "/")
            data = src.read(info)
            if name.endswith("/RUNTIME_CONFLICTS_V2_2.md"):
                history_name = name.rsplit("/", 1)[0] + "/history/RUNTIME_CONFLICTS_V2_2.md"
                dst.writestr(history_name, data)
                current_name = name[:-len("RUNTIME_CONFLICTS_V2_2.md")] + "RUNTIME_CONFLICTS_V2_3.md"
                current = data.decode("utf-8-sig").replace("V2.2", "V2.3").encode("utf-8")
                dst.writestr(current_name, current)
            else:
                dst.writestr(info, data)
    os.replace(temp, path)


def main() -> None:
    paths = sorted(BASE.glob("AREA_*_IMAGES_INPUT_V2_3.zip"))
    if len(paths) != 19:
        raise RuntimeError(f"expected 19 V2.3 archives, found {len(paths)}")
    for path in paths:
        normalize(path)
    print(f"normalized {len(paths)} archives")


if __name__ == "__main__":
    main()
