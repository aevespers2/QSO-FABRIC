#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main(a:list[str])->int:
 d=json.loads((R/'registry'/'formats.json').read_text())['families']
 if len(a)==1:
  for x in d:print(f"{x['name']}\t{x['extension']}\t{x['mutation_class']}")
  return 0
 q=a[1].lower()
 for x in d:
  if q in {x['name'].lower(),x['extension'].lower()}:print(json.dumps(x,indent=2,sort_keys=True));return 0
 return 1
if __name__=='__main__':raise SystemExit(main(sys.argv))
