#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import stat
import sys
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_PATH = "META-INF/qso-package.json"
MAX_ENTRIES = 256
MAX_MEMBER_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
ALLOWED_COMPRESSION = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
ALLOWED_MEDIA_TYPES = {"application/qso+json", "application/qso+cbor"}
MEDIA_TYPES = {".json": "application/qso+json", ".cbor": "application/qso+cbor"}


@dataclass(frozen=True)
class ValidatedEntry:
    path: str
    data: bytes
    media_type: str
    sha256: str


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_json(data: bytes) -> Any:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("manifest is not UTF-8") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError("invalid package manifest JSON") from exc


def _normalize_path(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("unsafe package path")
    if "\x00" in name or "\\" in name or name.startswith("/"):
        raise ValueError("unsafe package path")
    if re.match(r"^[A-Za-z]:", name):
        raise ValueError("unsafe package path")
    try:
        name.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError("unsafe package path") from exc
    if unicodedata.normalize("NFC", name) != name:
        raise ValueError("unsafe package path")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("unsafe package path")
    normalized = path.as_posix()
    if normalized != name or name.endswith("/"):
        raise ValueError("unsafe package path")
    return normalized


def _is_regular_member(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return mode == 0 or stat.S_ISREG(mode)


def _validate_archive_members(zf: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    infos = zf.infolist()
    if len(infos) > MAX_ENTRIES + 1:
        raise ValueError("too many package entries")
    members: dict[str, zipfile.ZipInfo] = {}
    casefolded: set[str] = set()
    total = 0
    for info in infos:
        name = _normalize_path(info.filename)
        folded = name.casefold()
        if name in members or folded in casefolded:
            raise ValueError("duplicate package entry")
        if info.is_dir() or not _is_regular_member(info):
            raise ValueError("unsupported package member type")
        if info.flag_bits & 0x1:
            raise ValueError("encrypted package entries are unsupported")
        if info.compress_type not in ALLOWED_COMPRESSION:
            raise ValueError("unsupported package compression")
        if info.file_size < 0 or info.file_size > MAX_MEMBER_BYTES:
            raise ValueError("oversized package member")
        total += info.file_size
        if total > MAX_TOTAL_BYTES:
            raise ValueError("oversized package")
        members[name] = info
        casefolded.add(folded)
    if list(name for name in members if name == MANIFEST_PATH) != [MANIFEST_PATH]:
        raise ValueError("package manifest missing")
    return members


def _validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    if not isinstance(manifest, dict):
        raise ValueError("invalid package manifest")
    if set(manifest) != {"format", "version", "entries"}:
        raise ValueError("invalid package manifest fields")
    if manifest["format"] != "QSO-PACKAGE" or manifest["version"] != "0.1.0":
        raise ValueError("unsupported package manifest")
    entries = manifest["entries"]
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise ValueError("invalid package manifest entries")
    validated: list[dict[str, Any]] = []
    seen: set[str] = set()
    casefolded: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "media_type", "sha256"}:
            raise ValueError("invalid package manifest entry")
        path = _normalize_path(entry["path"])
        folded = path.casefold()
        if path == MANIFEST_PATH or path in seen or folded in casefolded:
            raise ValueError("duplicate package manifest entry")
        size = entry["size"]
        if isinstance(size, bool) or not isinstance(size, int) or size < 0 or size > MAX_MEMBER_BYTES:
            raise ValueError("invalid package manifest size")
        media_type = entry["media_type"]
        expected_media_type = MEDIA_TYPES.get(PurePosixPath(path).suffix.lower())
        if media_type not in ALLOWED_MEDIA_TYPES or media_type != expected_media_type:
            raise ValueError("unsupported package media type")
        digest = entry["sha256"]
        if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError("invalid package manifest hash")
        validated.append(entry)
        seen.add(path)
        casefolded.add(folded)
    return validated


def verify_package(package: Path) -> list[ValidatedEntry]:
    try:
        with zipfile.ZipFile(package) as zf:
            members = _validate_archive_members(zf)
            manifest_info = members[MANIFEST_PATH]
            manifest = _strict_json(zf.read(manifest_info))
            entries = _validate_manifest(manifest)
            archive_paths = set(members) - {MANIFEST_PATH}
            manifest_paths = {entry["path"] for entry in entries}
            if archive_paths != manifest_paths:
                raise ValueError("incomplete package manifest")
            validated: list[ValidatedEntry] = []
            for entry in entries:
                info = members[entry["path"]]
                if info.file_size != entry["size"]:
                    raise ValueError("package member size mismatch")
                data = zf.read(info)
                if len(data) != entry["size"]:
                    raise ValueError("package member size mismatch")
                digest = "sha256:" + hashlib.sha256(data).hexdigest()
                if digest != entry["sha256"]:
                    raise ValueError("package member hash mismatch")
                validated.append(
                    ValidatedEntry(
                        path=entry["path"],
                        data=data,
                        media_type=entry["media_type"],
                        sha256=digest,
                    )
                )
            return validated
    except zipfile.BadZipFile as exc:
        raise ValueError("invalid package archive") from exc


def extract_verified(entries: list[ValidatedEntry], target: Path) -> None:
    target = target.resolve()
    if target.exists():
        if target.is_symlink() or not target.is_dir() or any(target.iterdir()):
            raise ValueError("output directory must be absent or empty")
    else:
        target.mkdir(parents=True)
    for entry in entries:
        destination = target.joinpath(*PurePosixPath(entry.path).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        cursor = destination.parent
        while cursor != target:
            if cursor.is_symlink():
                raise ValueError("unsafe output path")
            cursor = cursor.parent
        with destination.open("xb") as handle:
            handle.write(entry.data)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: qso_unpack.py INPUT.qsp OUTPUT_DIR", file=sys.stderr)
        return 2
    entries = verify_package(Path(argv[1]))
    extract_verified(entries, Path(argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
