from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from tender_intelligence_platform.database.models.ingestion_run import (
    IngestionRunORM,
)


class IngestionRunRepository:
    """
    Repository for ingestion run history.

    Deliberately used with its own short-lived session per call (see
    main.py's ingest_once) rather than sharing the main ingestion
    session: if the ingestion itself fails and its session is rolled
    back, the run record documenting that failure must still survive.
    """

    def __init__(self, session: Session):
        self._session = session

    def start_run(self) -> IngestionRunORM:
        """Record the start of a new ingestion run."""

        run = IngestionRunORM(
            started_at=datetime.now(timezone.utc),
            status="RUNNING",
        )

        self._session.add(run)
        self._session.flush()

        return run

    def complete_run(
        self,
        run_id: int,
        *,
        discovered: int,
        successful: int,
        failed: int,
        skipped: int,
    ) -> IngestionRunORM | None:
        """Mark a run as successfully completed with its final counts."""

        run = self._session.get(IngestionRunORM, run_id)

        if run is None:
            return None

        run.finished_at = datetime.now(timezone.utc)
        run.status = "SUCCESS"
        run.discovered = discovered
        run.successful = successful
        run.failed = failed
        run.skipped = skipped

        self._session.flush()

        return run

    def fail_run(
        self,
        run_id: int,
        error: str,
    ) -> IngestionRunORM | None:
        """Mark a run as failed with the error message."""

        run = self._session.get(IngestionRunORM, run_id)

        if run is None:
            return None

        run.finished_at = datetime.now(timezone.utc)
        run.status = "FAILED"
        run.error = error

        self._session.flush()

        return run

    def get_last_run(self) -> IngestionRunORM | None:
        """Return the most recently started ingestion run."""

        statement = (
            select(IngestionRunORM)
            .order_by(IngestionRunORM.started_at.desc())
            .limit(1)
        )

        return self._session.scalar(statement)