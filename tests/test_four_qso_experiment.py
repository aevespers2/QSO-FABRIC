from qso_runtime.four_qso_experiment import ExperimentLimits, run_experiment


def test_four_qso_experiment_is_deterministic() -> None:
    limits = ExperimentLimits(max_rounds=2, max_runtime_seconds=10)
    first = run_experiment("Build a safe QSO fabric", 42, limits)
    second = run_experiment("Build a safe QSO fabric", 42, limits)
    assert first == second
    assert first["ledger_valid"] is True
    assert set(first["qsos"]) == {"atlas", "nova", "orion", "lyra"}


def test_results_include_freeze_points_and_messages() -> None:
    report = run_experiment("Test bounded collaboration", 7, ExperimentLimits(max_rounds=1))
    for result in report["qsos"].values():
        assert len(result["freeze_points"]) == 3
        assert result["messages_sent"]
        assert result["messages_received"]
        assert result["final_proposal"]


def test_nova_requires_verification() -> None:
    report = run_experiment("Prepare release", 9, ExperimentLimits(max_rounds=1))
    assert "deterministic replay" in report["qsos"]["nova"]["final_proposal"].lower()
