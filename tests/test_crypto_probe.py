from __future__ import annotations

import unittest
from unittest.mock import patch

from qso_runtime.crypto_probe import probe_capabilities


class CryptoProbeTests(unittest.TestCase):
    def test_probe_is_fail_closed_for_production(self):
        with patch("qso_runtime.crypto_probe._module_available", return_value=False):
            report = probe_capabilities()
        self.assertFalse(report["ready_for_research"])
        self.assertFalse(report["ready_for_production"])
        self.assertEqual("qso.crypto.capability-probe.v1", report["schema"])

    def test_oqs_detection_enables_research_only(self):
        def available(name: str) -> bool:
            return name == "oqs"

        with patch("qso_runtime.crypto_probe._module_available", side_effect=available):
            report = probe_capabilities()
        self.assertTrue(report["ready_for_research"])
        self.assertFalse(report["ready_for_production"])
        kem = report["capabilities"][0]
        self.assertTrue(kem["available"])
        self.assertFalse(kem["production_accepted"])


if __name__ == "__main__":
    unittest.main()
