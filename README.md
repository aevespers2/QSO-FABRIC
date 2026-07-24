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

## Self-weighing warp-field experiment

The numerical-relativity experiment evaluates an explicit 3+1 metric ansatz, infers the stress-energy burden required by the Hamiltonian constraint, integrates signed and absolute mass-equivalent observables, checks momentum and asymptotic-boundary diagnostics, and performs bounded reproducible parameter learning.

```bash
python -m qso_runtime.warp_field_experiment \
  --extent 40 \
  --points 65 \
  --radius 10 \
  --sigma 0.8 \
  --velocity 0.05 \
  --iterations 12 \
  --target-mass 0 \
  --seed 2987 \
  --output artifacts/warp_field_report.json
```

The current backend is an Alcubierre-class flat-slice finite-difference solver. It reports the stress-energy required by that metric ansatz; it does not assert that the source can be physically constructed. The backend boundary is designed for replacement by a BSSN or CCZ4 evolution solver while preserving the experiment schema and audit trail.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
- Warp-field outputs are numerical model results, not evidence of a realizable propulsion system.
