#!/usr/bin/env python3
from __future__ import annotations
import json,sys,zipfile
from pathlib import Path
def main(a:list[str])->int:
 if len(a)!=3:print('usage: qso_pack.py INPUT_DIR OUTPUT.qsp',file=sys.stderr);return 2
 s=Path(a[1]);o=Path(a[2]);e=[]
 with zipfile.ZipFile(o,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for p in sorted(x for x in s.rglob('*') if x.is_file()):r=p.relative_to(s).as_posix();z.write(p,r);e.append(r)
  z.writestr('META-INF/qso-package.json',json.dumps({'format':'QSO-PACKAGE','version':'0.1.0','entries':e},sort_keys=True,indent=2)+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main(sys.argv))
