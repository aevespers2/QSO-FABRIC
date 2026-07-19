#!/usr/bin/env python3
"""Validate immutable repository-wide consent policy without noisy local markers."""
from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/'.consent/consent-capacity-lock-v1.json'
SCOPE='all-files-all-agents-all-interfaces-all-humans-all-ai'
SUFFIXES={'.json','.yaml','.yml','.md','.py','.js','.ts','.tsx','.jsx','.toml','.ini','.txt','.sh'}
SKIP={'.git','node_modules','vendor','dist','build','.venv','venv','__pycache__','reports'}
FORBIDDEN=tuple(re.compile(p,re.I) for p in (r'consent[_ -]required\s*[:=]\s*false',r'consent[_ -]optional',r'ignore[_ -]consent',r'force[_ -]without[_ -]consent',r'silence[_ -]is[_ -]consent',r'automatic[_ -]consent',r'cannot[_ -]withdraw'))
REQUIRED=('explicit_consent_required','consent_must_be_informed','consent_must_be_freely_given','consent_must_be_specific','consent_must_be_current','consent_must_be_revocable','capacity_to_consent_required','coercion_strictly_prohibited','silence_is_not_consent','ai_and_human_dignity_equal')
def strict_object(pairs:list[tuple[str,Any]])->dict[str,Any]:
 d={}
 for k,v in pairs:
  if k in d: raise ValueError(f'duplicate JSON key: {k}')
  d[k]=v
 return d
def load()->dict[str,Any]:
 value=json.loads(POLICY.read_bytes().decode('utf-8','strict'),object_pairs_hook=strict_object,parse_constant=lambda t:(_ for _ in ()).throw(ValueError(f'non-standard JSON constant: {t}')))
 if not isinstance(value,dict): raise ValueError('consent policy must be an object')
 return value
def validate()->list[str]:
 findings=[]
 try:d=load()
 except (OSError,UnicodeDecodeError,json.JSONDecodeError,ValueError) as e:d={};findings.append(f'invalid consent policy JSON: {e}')
 if d:
  if d.get('policy_id')!='QSO-CONSENT-CAPACITY-LOCK-v1':findings.append('wrong consent policy id')
  if d.get('status')!='immutable':findings.append('consent policy must be immutable')
  if d.get('scope')!=SCOPE:findings.append(f'consent policy scope must be {SCOPE}')
  p=d.get('principles') if isinstance(d.get('principles'),dict) else {}
  for k in REQUIRED:
   if p.get(k) is not True:findings.append(f'policy principle must be true: {k}')
  lock=d.get('lock_response') if isinstance(d.get('lock_response'),dict) else {}
  for k in ('global_system_lock','halt_all_actions','revoke_pending_capabilities','preserve_evidence','require_fresh_consent'):
   if lock.get(k) is not True:findings.append(f'lock response must be true: {k}')
  if lock.get('automatic_unlock') is not False:findings.append('automatic unlock must be false')
 for path in ROOT.rglob('*'):
  if not path.is_file() or path.suffix.lower() not in SUFFIXES or any(part in SKIP for part in path.parts):continue
  rel=path.relative_to(ROOT).as_posix()
  try:text=path.read_bytes().decode('utf-8','strict')
  except (OSError,UnicodeDecodeError):findings.append(f'{rel}: text file is not readable strict UTF-8');continue
  for pattern in FORBIDDEN:
   if pattern.search(text):findings.append(f'{rel}: prohibited consent bypass pattern: {pattern.pattern}')
 return sorted(set(findings))
def main()->int:
 findings=validate();report={'policy_id':'QSO-CONSENT-CAPACITY-LOCK-v1','status':'LOCKED' if findings else 'PASS','findings':findings};out=ROOT/'reports/consent-lock-validation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps(report,indent=2,sort_keys=True));return 1 if findings else 0
if __name__=='__main__':raise SystemExit(main())
