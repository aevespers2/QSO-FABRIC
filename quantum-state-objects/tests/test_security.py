from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads(
    (ROOT / "tests" / "fixtures" / "hostile-package-corpus.json").read_text(
        encoding="utf-8"
    )
)


def load_tool(name: str):
    path = ROOT / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PACK = load_tool("qso_pack")
UNPACK = load_tool("qso_unpack")
RESOURCE = "objects/example.qso.json"
DATA = b'{"kind":"QSO-CORE"}\n'


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def manifest(entries: list[dict[str, object]]) -> bytes:
    return (
        json.dumps(
            {"format": "QSO-PACKAGE", "version": "0.1.0", "entries": entries},
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def regular_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    info.external_attr = 0o100644 << 16
    return info


def write_case(path: Path, mutation: str) -> None:
    entry = {
        "path": RESOURCE,
        "size": len(DATA),
        "media_type": "application/qso+json",
        "sha256": digest(DATA),
    }
    entries = [entry]
    resource_name = RESOURCE
    resource_data = DATA
    include_manifest = True
    raw_manifest: bytes | None = None
    extra_members: list[tuple[zipfile.ZipInfo | str, bytes]] = []

    if mutation == "parent_path":
        resource_name = "../escape.qso.json"
        entry["path"] = resource_name
    elif mutation == "absolute_path":
        resource_name = "/escape.qso.json"
        entry["path"] = resource_name
    elif mutation == "backslash_path":
        resource_name = "objects\\escape.qso.json"
        entry["path"] = resource_name
    elif mutation == "duplicate_entry":
        extra_members.append((regular_info(RESOURCE), DATA))
    elif mutation == "casefold_collision":
        extra_members.append((regular_info("OBJECTS/example.qso.json"), DATA))
        entries.append(
            {
                "path": "OBJECTS/example.qso.json",
                "size": len(DATA),
                "media_type": "application/qso+json",
                "sha256": digest(DATA),
            }
        )
    elif mutation == "symlink_entry":
        symlink = zipfile.ZipInfo(RESOURCE)
        symlink.create_system = 3
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        resource_name = ""
        extra_members.append((symlink, b"target"))
    elif mutation == "missing_manifest":
        include_manifest = False
    elif mutation == "duplicate_manifest_key":
        raw_manifest = (
            b'{"format":"QSO-PACKAGE","format":"QSO-PACKAGE",'
            b'"version":"0.1.0","entries":[]}\n'
        )
    elif mutation == "hash_mismatch":
        entry["sha256"] = "sha256:" + "0" * 64
    elif mutation == "size_mismatch":
        entry["size"] = len(DATA) + 1
    elif mutation == "incomplete_manifest":
        entries = []
    elif mutation == "unsupported_media_type":
        entry["media_type"] = "text/html"
    elif mutation == "oversized_member":
        resource_data = b"x" * (UNPACK.MAX_MEMBER_BYTES + 1)
        entry["size"] = len(resource_data)
        entry["sha256"] = digest(resource_data)
    elif mutation != "none":
        raise AssertionError(f"unknown mutation {mutation}")

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        if resource_name:
            archive.writestr(regular_info(resource_name), resource_data)
        for info, data in extra_members:
            archive.writestr(info, data)
        if include_manifest:
            archive.writestr(
                regular_info(UNPACK.MANIFEST_PATH), raw_manifest or manifest(entries)
            )


class PackageBoundaryTests(unittest.TestCase):
    def test_hostile_corpus_fails_before_output_creation(self):
        self.assertEqual(CORPUS["format"], "QSO-HOSTILE-PACKAGE-CORPUS")
        identifiers = [case["id"] for case in CORPUS["cases"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for case in CORPUS["cases"]:
                with self.subTest(case=case["id"]):
                    package = root / f"{case['id']}.qsp"
                    output = root / f"{case['id']}-out"
                    write_case(package, case["mutation"])
                    if case.get("accepted"):
                        self.assertEqual(
                            UNPACK.main(["qso_unpack", str(package), str(output)]), 0
                        )
                        self.assertEqual((output / RESOURCE).read_bytes(), DATA)
                    else:
                        with self.assertRaisesRegex(ValueError, case["error"]):
                            UNPACK.main(["qso_unpack", str(package), str(output)])
                        self.assertFalse(output.exists())

    def test_deterministic_pack_and_verified_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            resource = source / RESOURCE
            resource.parent.mkdir()
            resource.write_bytes(DATA)
            first = root / "first.qsp"
            second = root / "second.qsp"
            PACK.build_package(source, first)
            PACK.build_package(source, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            output = root / "output"
            self.assertEqual(
                UNPACK.main(["qso_unpack", str(first), str(output)]), 0
            )
            self.assertEqual((output / RESOURCE).read_bytes(), DATA)

    def test_unpack_rejects_symlink_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "valid.qsp"
            write_case(package, "none")
            real_output = root / "real-output"
            real_output.mkdir()
            linked_output = root / "linked-output"
            try:
                linked_output.symlink_to(real_output, target_is_directory=True)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "unsafe output path"):
                UNPACK.main(["qso_unpack", str(package), str(linked_output)])
            self.assertFalse((real_output / RESOURCE).exists())

    def test_pack_rejects_symlink_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            target = root / "target.json"
            target.write_bytes(DATA)
            link = source / "link.json"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "symbolic links"):
                PACK.build_package(source, root / "out.qsp")


if __name__ == "__main__":
    unittest.main()
