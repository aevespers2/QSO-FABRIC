from __future__ import annotations
import importlib.util,tempfile,unittest,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_traversal(self):
  p=R/'tools'/'qso_unpack.py';s=importlib.util.spec_from_file_location('u',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  with tempfile.TemporaryDirectory() as d:
   z=Path(d)/'bad.qsp'
   with zipfile.ZipFile(z,'w') as q:q.writestr('../escape','x')
   with self.assertRaises(ValueError):m.main(['u',str(z),str(Path(d)/'out')])
if __name__=='__main__':unittest.main()
