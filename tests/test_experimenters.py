from qso_runtime.experimenters import CollectiveLimits, ROLE_ORDER, run_collective


def test_collective_is_deterministic() -> None:
    limits = CollectiveLimits(max_rounds=2)
    first = run_collective("Design a bounded scientific instrument", limits)
    second = run_collective("Design a bounded scientific instrument", limits)
    assert first == second
    assert first["ledger_valid"] is True
    assert tuple(first["workflow"]) == ROLE_ORDER


def test_collective_includes_inventor_and_futurist() -> None:
    report = run_collective("Explore resilient research infrastructure", CollectiveLimits(max_rounds=1))
    assert "inventor" in report["experimenters"]
    assert "futurist" in report["experimenters"]
    assert "novel" in report["experimenters"]["inventor"]["contributions"][0].lower()
    assert "scenarios" in report["experimenters"]["futurist"]["contributions"][0].lower()


def test_every_role_is_bounded_and_frozen() -> None:
    limits = CollectiveLimits(max_rounds=1, max_messages_per_role=1, max_message_chars=120)
    report = run_collective("Test bounded collaboration", limits)
    assert report["human_review_required"] is True
    for result in report["experimenters"].values():
        assert len(result["freeze_points"]) == 3
        assert len(result["messages_sent"]) <= 1
        assert len(result["messages_received"]) <= 1
        assert all(len(message["text"]) <= 120 for message in result["messages_sent"])
        assert all(len(message["text"]) <= 120 for message in result["messages_received"])
        assert all(len(contribution) <= 120 for contribution in result["contributions"])


def test_message_limit_drops_are_audited() -> None:
    report = run_collective(
        "Run enough rounds to exceed the message quota",
        CollectiveLimits(max_rounds=3, max_messages_per_role=1, max_message_chars=200),
        roles=("futurist", "inventor"),
    )
    dropped = [event for event in report["events"] if event["kind"] == "message_dropped"]
    assert dropped
    assert all(event["payload"]["reason"] in {"sender_limit", "recipient_limit"} for event in dropped)


def test_subset_workflow_is_supported() -> None:
    report = run_collective(
        "Prototype a measurement method",
        CollectiveLimits(max_rounds=1),
        roles=("futurist", "inventor", "experimentalist", "skeptic", "archivist"),
    )
    assert report["workflow"] == ["futurist", "inventor", "experimentalist", "skeptic", "archivist"]
    review_events = [event for event in report["events"] if event["kind"] == "human_review_required"]
    assert review_events[0]["actor"] == "fabric"
