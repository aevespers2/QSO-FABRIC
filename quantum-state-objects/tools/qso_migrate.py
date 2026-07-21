#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
def migrate(v:dict,t:str)->dict:
 c=v.get('qso',{}).get('format_version')
 if c==t:return v
 if c=='0.1.0' and t=='0.2.0':v['qso']['format_version']=t;v['qso'].setdefault('migration_history',[]).append({'from':'0.1.0','to':'0.2.0'});return v
 raise ValueError(f'unsupported migration {c} -> {t}')
def main(a:list[str])->int:
 if len(a)!=4:print('usage: qso_migrate.py INPUT TARGET OUTPUT',file=sys.stderr);return 2
 v=migrate(json.loads(Path(a[1]).read_text()),a[2]);Path(a[3]).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');return 0
if __name__=='__main__':raise SystemExit(main(sys.argv))
