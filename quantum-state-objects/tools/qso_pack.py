#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

MANIFEST_PATH = "META-INF/qso-package.json"
MAX_ENTRIES = 256
MAX_MEMBER_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MEDIA_TYPES = {
    ".json": "application/qso+json",
    ".cbor": "application/qso+cbor",
}


def _media_type(path: str) -> str:
    suffix = PurePosixPath(path).suffix.lower()
    try:
        return MEDIA_TYPES[suffix]
    except KeyError as exc:
        raise ValueError(f"unsupported package media type for {path}") from exc


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def build_package(source: Path, output: Path) -> None:
    source = source.resolve(strict=True)
    output = output.resolve()
    if not source.is_dir():
        raise ValueError("input must be a directory")
    if source == output or source in output.parents:
        raise ValueError("output package must be outside input directory")
    files: list[tuple[str, bytes]] = []
    total = 0
    for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix()):
        if path.is_symlink():
            raise ValueError("symbolic links are not packageable")
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        if relative == MANIFEST_PATH:
            raise ValueError("input may not provide the package manifest")
        data = path.read_bytes()
        if len(data) > MAX_MEMBER_BYTES:
            raise ValueError("oversized package member")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise ValueError("oversized package")
        files.append((relative, data))
    if len(files) > MAX_ENTRIES:
        raise ValueError("too many package entries")
    entries = [
        {
            "path": relative,
            "size": len(data),
            "media_type": _media_type(relative),
            "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        }
        for relative, data in files
    ]
    manifest = json.dumps(
        {"format": "QSO-PACKAGE", "version": "0.1.0", "entries": entries},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8") + b"\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for relative, data in files:
            archive.writestr(_zip_info(relative), data)
        archive.writestr(_zip_info(MANIFEST_PATH), manifest)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: qso_pack.py INPUT_DIR OUTPUT.qsp", file=sys.stderr)
        return 2
    build_package(Path(argv[1]), Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
