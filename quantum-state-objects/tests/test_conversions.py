from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def canonical_hash(value: dict) -> str:
    clone = json.loads(json.dumps(value))
    clone["qso"].pop("content_hash", None)
    encoded = json.dumps(
        clone,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class ConversionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(
            (ROOT / "conversions" / "conversion-registry.json").read_text(encoding="utf-8")
        )

    def test_registered_sources_are_preserved_and_match_digest(self) -> None:
        for item in self.registry["conversions"]:
            source = REPO / item["source"]["path"]
            self.assertTrue(source.is_file())
            digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(item["source"]["content_hash"], digest)

    def test_registered_targets_match_content_hash(self) -> None:
        for item in self.registry["conversions"]:
            target = REPO / item["target"]["path"]
            value = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(item["target"]["object_id"], value["qso"]["object_id"])
            self.assertEqual(value["qso"]["content_hash"], canonical_hash(value))

    def test_every_conversion_has_provenance(self) -> None:
        for item in self.registry["conversions"]:
            provenance = REPO / item["provenance"]
            self.assertTrue(provenance.is_file())
            value = json.loads(provenance.read_text(encoding="utf-8"))
            self.assertEqual("QSO-PROVENANCE", value["qso"]["format"])


if __name__ == "__main__":
    unittest.main()
