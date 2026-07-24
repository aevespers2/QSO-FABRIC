import math

import pytest

import qso_mcp_server.runtime as runtime_module
from qso_mcp_server.runtime import QSOService


def test_service_runs_verifies_and_replays() -> None:
    service = QSOService(max_jobs=4)
    job = service.run("Test bounded simulation", seed=42, rounds=2)

    assert job["status"] == "completed"
    assert job["report"]["ledger_valid"] is True
    verification = service.verify_job(job["job_id"])
    assert verification["valid"] is True
    replay = service.replay(job["job_id"])
    assert replay["deterministic_match"] is True
    assert replay["guaranteed"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed", True),
        ("rounds", True),
        ("max_messages_per_qso", False),
        ("max_message_chars", True),
    ],
)
def test_service_rejects_boolean_integer_coercion(field: str, value: bool) -> None:
    service = QSOService()
    kwargs = {field: value}
    with pytest.raises(TypeError):
        service.run("invalid", **kwargs)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True, "10"])
def test_service_rejects_non_finite_or_coercive_runtime(value: object) -> None:
    service = QSOService()
    expected = TypeError if isinstance(value, (bool, str)) else ValueError
    with pytest.raises(expected):
        service.run("invalid", max_runtime_seconds=value)


@pytest.mark.parametrize("value", [None, 1, True, "", "   ", "x" * 8193, "nul\x00value"])
def test_service_rejects_malformed_objective(value: object) -> None:
    service = QSOService()
    with pytest.raises((TypeError, ValueError)):
        service.run(value)


def test_returned_records_cannot_mutate_stored_evidence() -> None:
    service = QSOService()
    job = service.run("Mutation resistance", seed=7, rounds=1)
    job["report"]["ledger_valid"] = False
    job["request"]["objective"] = "tampered"
    job["result_digest"] = "0" * 64

    stored = service.get_job(job["job_id"])
    assert stored["report"]["ledger_valid"] is True
    assert stored["request"]["objective"] == "Mutation resistance"
    assert service.verify_job(job["job_id"])["valid"] is True

    stored["report"]["ledger_valid"] = False
    assert service.verify_job(job["job_id"])["valid"] is True


def test_job_listing_omits_large_report_and_returns_detached_data() -> None:
    service = QSOService()
    job = service.run("List metadata only", rounds=1)

    jobs = service.list_jobs()
    assert len(jobs) == 1
    assert "report" not in jobs[0]
    jobs[0]["request"]["objective"] = "tampered"
    assert service.get_job(job["job_id"])["request"]["objective"] == "List metadata only"


@pytest.mark.parametrize("value", [True, 0, 1025, 1.5, "4"])
def test_max_jobs_is_strict_and_bounded(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        QSOService(max_jobs=value)


@pytest.mark.parametrize("value", [True, 0, 129, 1.5, "2"])
def test_list_limit_is_strict_and_bounded(value: object) -> None:
    service = QSOService(max_jobs=128)
    with pytest.raises((TypeError, ValueError)):
        service.list_jobs(limit=value)


def test_include_report_requires_exact_boolean() -> None:
    service = QSOService()
    job = service.run("Boolean boundary", rounds=1)
    with pytest.raises(TypeError):
        service.get_job(job["job_id"], include_report=1)


@pytest.mark.parametrize("value", ["", "not-a-uuid", "A4D5933F-76C4-4C24-AD45-4AA8325B1B04", 7])
def test_job_id_requires_canonical_uuid(value: object) -> None:
    service = QSOService()
    with pytest.raises((TypeError, ValueError)):
        service.get_job(value)


def test_non_boolean_ledger_claim_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_report(*args: object, **kwargs: object) -> dict[str, object]:
        return {"ledger_valid": "yes", "final_event_hash": "a" * 64}

    monkeypatch.setattr(runtime_module, "run_experiment", bad_report)
    service = QSOService()
    with pytest.raises(ValueError):
        service.run("Reject truthy ledger claim")
    failed = service.list_jobs()[0]
    assert failed["status"] == "failed"
    assert failed["error"] == "simulation execution failed"
    assert "report" not in failed


def test_non_finite_report_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_report(*args: object, **kwargs: object) -> dict[str, object]:
        return {
            "ledger_valid": True,
            "final_event_hash": "a" * 64,
            "value": math.nan,
        }

    monkeypatch.setattr(runtime_module, "run_experiment", bad_report)
    with pytest.raises(ValueError):
        QSOService().run("Reject non-finite report")


def test_capacity_evicts_only_terminal_jobs() -> None:
    service = QSOService(max_jobs=1)
    first = service.run("first", rounds=1)
    second = service.run("second", rounds=1)
    assert first["job_id"] != second["job_id"]
    with pytest.raises(KeyError):
        service.get_job(first["job_id"])
    assert service.get_job(second["job_id"])["status"] == "completed"
