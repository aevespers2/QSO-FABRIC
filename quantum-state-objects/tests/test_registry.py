from __future__ import annotations
import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_unique(self):
  d=json.loads((R/'registry'/'formats.json').read_text())['families'];n=[x['name'] for x in d];e=[x['extension'] for x in d];self.assertEqual(len(n),len(set(n)));self.assertEqual(len(e),len(set(e)))
if __name__=='__main__':unittest.main()
