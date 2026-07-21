# Streaming

QSO streams are ordered frames with stream identifier, monotonic sequence number, frame type, payload length, payload hash, and optional previous-frame hash. Receivers detect truncation, replay, reordering, and conflicting sequence numbers. Snapshot frames establish recovery points; event and delta frames remain append-only.
