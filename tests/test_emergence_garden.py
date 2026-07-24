from qso_runtime.emergence_garden import EmergenceGarden, Evidence, GrowthStage


def supporting(index: int, *, reproducible: bool = False) -> Evidence:
    return Evidence(
        source=f"experiment-{index}",
        summary=f"supporting observation {index}",
        confidence=0.9,
        supports=True,
        reproducible=reproducible,
        evidence_id=f"e-{index}",
    )


def test_growth_lifecycle_reaches_flower() -> None:
    garden = EmergenceGarden()
    idea = garden.plant("Adaptive resonance", "Bounded resonance improves repair.", idea_id="idea-1")

    assert idea.stage is GrowthStage.SEED

    for index in range(1, 9):
        garden.add_evidence("idea-1", supporting(index, reproducible=index <= 3))

    assert idea.stage is GrowthStage.FLOWER
    assert idea.support_score > 0.8
    assert garden.verify_ledger()


def test_failed_path_is_preserved_and_can_be_revived() -> None:
    garden = EmergenceGarden()
    idea = garden.plant("Rejected path", "A deliberately uncertain proposal.", idea_id="idea-2")
    garden.add_evidence(
        "idea-2",
        Evidence(
            source="falsification-run",
            summary="The predicted effect was absent.",
            confidence=0.95,
            supports=False,
            reproducible=True,
            evidence_id="negative-1",
        ),
    )

    garden.mark_dead_branch("idea-2", "Falsified under the current protocol")

    assert idea.stage is GrowthStage.DEAD_BRANCH
    assert idea.archived_reason is not None
    assert "idea-2" in garden.ideas
    assert garden.snapshot()["event_count"] == 3

    garden.add_evidence("idea-2", supporting(2, reproducible=True))
    assert idea.stage is GrowthStage.DEAD_BRANCH

    garden.revive("idea-2", "New instrumentation justifies retesting")
    assert idea.stage is GrowthStage.SEED
    assert idea.archived_reason is None
    assert garden.verify_ledger()


def test_snapshot_is_deterministically_ordered() -> None:
    garden = EmergenceGarden()
    garden.plant("Second", "Second hypothesis", idea_id="b")
    garden.plant("First", "First hypothesis", idea_id="a")

    snapshot = garden.snapshot()

    assert snapshot["schema"] == "qso.emergence-garden/v1"
    assert [item["idea_id"] for item in snapshot["ideas"]] == ["a", "b"]
    assert snapshot["ledger_head"] != "GENESIS"
