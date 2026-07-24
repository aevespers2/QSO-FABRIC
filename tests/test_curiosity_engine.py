from qso_runtime.curiosity_engine import CuriosityLimits, plan_expeditions, run_curiosity_engine


def test_curiosity_engine_is_deterministic() -> None:
    limits = CuriosityLimits(max_expeditions=3, max_rounds_per_expedition=1)
    first = run_curiosity_engine("Explore resilient QSO memory", seed=42, limits=limits)
    second = run_curiosity_engine("Explore resilient QSO memory", seed=42, limits=limits)
    assert first == second
    assert first["ledger_valid"] is True


def test_expeditions_are_ranked_and_bounded() -> None:
    report = run_curiosity_engine(
        "Find contradictions in the QSO ontology",
        seed=7,
        limits=CuriosityLimits(max_expeditions=2, max_rounds_per_expedition=1),
    )
    assert len(report["expeditions"]) == 2
    scores = [item["score"]["total"] for item in report["expeditions"]]
    assert scores == sorted(scores, reverse=True)
    assert report["human_review_required"] is True
    assert report["network_authority"] is False
    assert report["execution_authority"] is False


def test_planner_emits_unique_expeditions() -> None:
    expeditions = plan_expeditions(
        "Design a falsifiable emergence experiment",
        seed=99,
        limits=CuriosityLimits(max_expeditions=4),
    )
    assert len({item.expedition_id for item in expeditions}) == 4
    assert len({item.expedition_type for item in expeditions}) == 4


def test_invalid_expedition_count_fails_closed() -> None:
    try:
        plan_expeditions("objective", limits=CuriosityLimits(max_expeditions=5))
    except ValueError as exc:
        assert "max_expeditions" in str(exc)
    else:
        raise AssertionError("expected ValueError")
