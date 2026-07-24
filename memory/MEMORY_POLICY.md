# Persistent Memory Policy

This directory is an explicit, versioned memory layer for the QSO ecosystem.

## Core rule

Content the user has explicitly said **not to store**, **not to remember**, **not to retain**, or **not to persist** must never be written here, even if a later message appears to request bulk storage of everything. A later request may change this only when it clearly identifies the specific previously excluded item and explicitly revokes the exclusion for that item.

## Default exclusions

Do not store raw or identifying details involving:

- passwords, tokens, credentials, recovery codes, cryptographic secrets
- Social Security numbers, government identifiers, private addresses, or private contact details
- medical records or diagnoses
- privileged legal communications or sealed records
- intimate or sexual material
- allegations about private individuals presented as unverified fact
- material explicitly labeled ephemeral, off-record, private, confidential, or not for persistence

## Permitted durable memory

Store only information that is useful for continuity and has a clear project purpose, such as:

- repository architecture and technical decisions
- accepted terminology and schemas
- project milestones and unresolved engineering questions
- stable response preferences
- public citations and verified public facts
- user-approved summaries that avoid unnecessary personal detail

## Consent and correction

Each memory record must include provenance, confidence, sensitivity, and a deletion or correction path. User corrections supersede older records. Ambiguous or disputed statements must be labeled as such and must not be converted into asserted fact.

## Redaction ledger

Excluded content may be represented only by a non-reconstructive marker, for example:

```json
{
  "status": "excluded",
  "reason": "user_requested_non_persistence",
  "content": null
}
```

The marker must not contain quotations, summaries, hashes, embeddings, filenames, or metadata that could reconstruct or identify the excluded content.
