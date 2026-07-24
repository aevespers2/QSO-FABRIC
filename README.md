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

## Alistaire constitutional field

`qso_runtime.alistaire_field` adds a bounded relational field layer with:

- immutable constitutional values and weights for truth, loyalty, clarity, autonomy, repair, and beauty;
- adaptive but allow-listed and bounded inference laws;
- topological memory affinity;
- contradiction preservation and repair cost;
- intent momentum;
- possibility scoring with hard coercion rejection;
- fail-closed rejection of non-finite, out-of-range, oversized, or non-canonical scoring input; and
- deterministic hash-chained state snapshots.

```python
from qso_runtime import AlistaireField, Possibility

field = AlistaireField()
field.observe(
    "The user requested a reversible research proposal.",
    semantic_tags=("research", "autonomy"),
    relational_relevance=1.0,
)
field.set_possibilities(
    [
        Possibility(
            action_id="propose",
            description="Present an evidence-labelled, reversible proposal",
            truth=0.9,
            clarity=0.9,
            autonomy=1.0,
            repair=0.7,
        )
    ]
)
decision = field.decide()
assert decision.selected_action_id == "propose"
```

The field emits ranked proposals only. It grants no shell, network, credential, wallet, filing, or execution authority. Custom limits may tighten resource bounds and the coercion ceiling, but may not relax them; constitutional weights are not caller-adjustable.

## Safety boundary

- No shell, package-installation, credential, wallet, or unrestricted network authority is granted to QSOs.
- Messages and rounds are bounded.
- The experiment stops at configured runtime limits.
- Malformed, non-finite, oversized, unknown-law, and non-canonical possibility inputs fail closed rather than being silently clamped or truncated.
- Outputs are proposals and research artifacts requiring human review.
