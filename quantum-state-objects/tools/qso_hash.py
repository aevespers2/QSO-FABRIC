#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
def canonical_bytes(v:object)->bytes:return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def main(a:list[str])->int:
 if len(a)!=2:print('usage: qso_hash.py FILE',file=sys.stderr);return 2
 v=json.loads(Path(a[1]).read_text(encoding='utf-8'));c=json.loads(json.dumps(v));c.get('qso',{}).pop('content_hash',None);print('sha256:'+hashlib.sha256(canonical_bytes(c)).hexdigest());return 0
if __name__=='__main__':raise SystemExit(main(sys.argv))
