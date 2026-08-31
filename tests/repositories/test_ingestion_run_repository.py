from tender_intelligence_platform.repositories.ingestion_run_repository import (
    IngestionRunRepository,
)


def test_start_run_creates_running_record(db_session):
    repository = IngestionRunRepository(db_session)

    run = repository.start_run()
    db_session.commit()

    assert run.id is not None
    assert run.status == "RUNNING"
    assert run.finished_at is None


def test_complete_run_records_final_counts(db_session):
    repository = IngestionRunRepository(db_session)

    run = repository.start_run()
    db_session.commit()

    updated = repository.complete_run(
        run.id,
        discovered=10,
        successful=7,
        failed=1,
        skipped=2,
    )
    db_session.commit()

    assert updated.status == "SUCCESS"
    assert updated.finished_at is not None
    assert updated.discovered == 10
    assert updated.successful == 7
    assert updated.failed == 1
    assert updated.skipped == 2


def test_fail_run_records_error(db_session):
    repository = IngestionRunRepository(db_session)

    run = repository.start_run()
    db_session.commit()

    updated = repository.fail_run(run.id, error="Homepage unreachable")
    db_session.commit()

    assert updated.status == "FAILED"
    assert updated.finished_at is not None
    assert updated.error == "Homepage unreachable"


def test_get_last_run_returns_most_recent(db_session):
    repository = IngestionRunRepository(db_session)

    first = repository.start_run()
    db_session.commit()
    repository.complete_run(
        first.id,
        discovered=1,
        successful=1,
        failed=0,
        skipped=0,
    )
    db_session.commit()

    second = repository.start_run()
    db_session.commit()

    last_run = repository.get_last_run()

    assert last_run is not None
    assert last_run.id == second.id
    assert last_run.status == "RUNNING"


def test_complete_run_returns_none_for_unknown_id(db_session):
    repository = IngestionRunRepository(db_session)

    result = repository.complete_run(
        999999999,
        discovered=0,
        successful=0,
        failed=0,
        skipped=0,
    )

    assert result is None 