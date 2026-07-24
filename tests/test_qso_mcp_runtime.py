from qso_mcp_server.runtime import QSOService


def test_service_runs_verifies_and_replays() -> None:
    service = QSOService(max_jobs=4)
    job = service.run("Test bounded simulation", seed=42, rounds=2)

    assert job["status"] == "completed"
    assert job["report"]["ledger_valid"] is True
    assert service.verify_job(job["job_id"])["valid"] is True
    assert service.replay(job["job_id"])["deterministic_match"] is True


def test_service_rejects_out_of_bounds_limits() -> None:
    service = QSOService()

    try:
        service.run("invalid", rounds=0)
    except ValueError as exc:
        assert "rounds" in str(exc)
    else:
        raise AssertionError("expected invalid rounds to be rejected")


def test_job_listing_omits_large_report() -> None:
    service = QSOService()
    service.run("List metadata only", rounds=1)

    jobs = service.list_jobs()
    assert len(jobs) == 1
    assert "report" not in jobs[0]
