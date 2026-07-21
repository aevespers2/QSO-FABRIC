from __future__ import annotations
import json,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_profiles(self):
  n=[]
  for p in (R/'profiles').glob('*.json'):
   v=json.loads(p.read_text());n.append(v['profile']);self.assertIn('QSO-CORE',v['required_formats'])
  self.assertEqual(len(n),len(set(n)))
if __name__=='__main__':unittest.main()
