# Canonicalization

QSO JSON authoring objects use deterministic UTF-8 serialization with lexicographically sorted object keys, no insignificant whitespace, finite JSON numbers only, and preserved array order. Production conformance targets RFC 8785. The top-level `qso.content_hash` field is omitted while calculating an object's own hash. Signatures bind format, version, schema, object identifier, canonicalization algorithm, hash algorithm, and content hash.
