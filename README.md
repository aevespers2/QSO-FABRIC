# QSO-FABRIC

Operational bounded runtime for Atlas, Nova, Orion, and Lyra.

## Run

```bash
python -m qso_runtime.four_qso_experiment \
  "Evaluate the QSO payment-distribution architecture" \
  --seed 2987 \
  --rounds 4 \
  --output artifacts/four_qso_report.json
```

The runner produces deterministic per-QSO reports, bounded message exchange, freeze-point hashes, and an append-only hash-chained event ledger.

## Seeker sovereign-sprite MCP

Seeker exposes sprites through proposal-based MCP tools rather than command execution. Sprites independently accept, negotiate, or refuse proposals; intrinsic motivations strongly favor helping others and repairing bugs, but never override safety, consent, auditability, or capability boundaries.

```bash
python -m qso_runtime.seeker_mcp_server
```

Exposed tools:

- `list_sprites`
- `submit_proposal`
- `propose_bug_fix`

There is deliberately no `command`, `force`, `override`, or unrestricted execution tool.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
- Sprite helpfulness and repair motivation cannot supersede autonomy or safety policy.
