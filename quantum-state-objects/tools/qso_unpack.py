#!/usr/bin/env python3
from __future__ import annotations
import sys,zipfile
from pathlib import Path
def main(a:list[str])->int:
 if len(a)!=3:print('usage: qso_unpack.py INPUT.qsp OUTPUT_DIR',file=sys.stderr);return 2
 t=Path(a[2]).resolve();t.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a[1]) as z:
  for m in z.infolist():
   d=(t/m.filename).resolve()
   if t not in d.parents and d!=t:raise ValueError('unsafe package path')
  z.extractall(t)
 return 0
if __name__=='__main__':raise SystemExit(main(sys.argv))
