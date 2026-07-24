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

## Laser-refraction angular-momentum simulator

The simulation-only laser module couples Snell refraction, photon linear momentum, orbital/spin angular momentum, an offset-interface torque, and a reduced rotational plasma model. It records deterministic time-series output and a SHA-256 report identity while keeping the fusion quantity explicitly labeled as a normalized research proxy rather than an engineering yield forecast.

```bash
python -m qso_runtime.laser_refraction_fusion \
  --power-w 5000 \
  --wavelength-m 1.064e-9 \
  --incidence-deg 30 \
  --n-in 1.0 \
  --n-out 1.5 \
  --pulse-s 5e-9 \
  --topological-charge 2 \
  --helicity 1 \
  --temperature-kev 10 \
  --density-m3 1e26 \
  --reaction DT \
  --momentum vacuum \
  --output artifacts/laser_refraction_fusion.json
```

The optical momentum convention can be selected as `abraham`, `minkowski`, or `vacuum`, allowing uncertainty sweeps without silently choosing one matter-momentum interpretation.

Run the simulator tests with:

```bash
python -m unittest tests.test_laser_refraction_fusion
```

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Outputs are proposals and research artifacts requiring human review.
- The laser/fusion module is a bounded numerical research surrogate, not an apparatus specification, control system, validated plasma model, or fusion-yield predictor.
