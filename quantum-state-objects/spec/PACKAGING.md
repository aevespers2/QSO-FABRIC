# Packaging

A `.qsp` development package is a deterministic archive containing QSO resources and `META-INF/qso-package.json`. Entries use relative UTF-8 paths and may not be absolute, traverse parent directories, or resolve through symbolic links. Production manifests record each entry's size, media type, object identifier, and content hash.
