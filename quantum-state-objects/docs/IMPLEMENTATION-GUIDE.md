# Implementation Guide

1. Parse strict UTF-8 without duplicate keys or non-finite numbers.
2. Validate the common envelope and family schema.
3. Verify format registry consistency.
4. Canonicalize and verify content hash.
5. Resolve required references.
6. Apply profile and governance rules.
7. Verify signatures before exposing capabilities.
8. Record migrations and mutations in provenance.

The included Python utilities are development references, not yet a hardened production SDK.
