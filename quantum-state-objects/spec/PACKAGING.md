# Packaging

A `.qsp` development package is a deterministic ZIP archive containing QSO resources and exactly one `META-INF/qso-package.json` manifest. Packaging is validation-only infrastructure; acceptance of an archive does not establish signer authority, resolve references, execute content, authorize mutation, or prove that a resource is safe for a production runtime.

## Manifest contract

The version `0.1.0` manifest contains only `format`, `version`, and `entries`. Every resource entry contains exactly:

- `path`: a normalized relative UTF-8 POSIX path;
- `size`: the exact uncompressed byte count;
- `media_type`: an allowed QSO JSON or CBOR media type consistent with the path extension;
- `sha256`: the lowercase `sha256:<hex>` digest of the exact resource bytes.

The archive resource set and manifest resource set must match exactly. Missing, extra, duplicate, case-fold-colliding, or manifest-self-referential entries fail closed.

## Pre-extraction boundary

An unpacker must validate the complete central directory and manifest before creating the destination directory or writing any resource. It rejects:

- absolute, parent-traversing, backslash, drive-qualified, non-normalized, empty, or NUL-containing paths;
- duplicate entries, case-fold collisions, directory entries, symbolic links, special files, encryption, and unsupported compression;
- more than 256 resources, resources larger than 4 MiB, or packages larger than 16 MiB uncompressed;
- missing or malformed manifests, duplicate JSON keys, non-finite JSON values, unknown fields, unsupported versions, invalid sizes, unsupported media types, and invalid hashes;
- incomplete bundles and any resource whose archive size, extracted byte count, or SHA-256 digest differs from the manifest.

Extraction is manual after validation rather than `extractall`. The output directory must be absent or empty, and destination parents may not be symbolic links.

## Determinism

The reference packer sorts resources by normalized path, fixes ZIP timestamps and regular-file permissions, uses a compact canonical manifest representation, and refuses source symbolic links or an output path inside the input tree. Identical accepted inputs therefore produce identical package bytes with the supported Python ZIP implementation.

The synthetic hostile-package corpus exercises traversal, absolute and backslash paths, duplicate members, case-fold collisions, symbolic links, missing and duplicate-key manifests, hash and size mismatch, incomplete manifests, unsupported media types, and oversized members. These fixtures prove only the bounded parser and extraction boundary.
