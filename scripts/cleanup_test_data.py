"""
Purge test-data tenders (and their cascade-deleted evaluations).

Test data is identified by tender_id starting with "TEST-" — the
prefix used by tests/conftest.py's make_tender() fixture, and by the
"TEST-EVAL-..." rows from earlier manual API testing (architecture
doc section 23). Both are covered by the same prefix check.

SAFE BY DEFAULT: running this with no flags only prints what would be
deleted. Nothing is ever deleted without --confirm AND typing DELETE
at the interactive prompt.

Usage:
    Dry run (default — deletes nothing):
        uv run python scripts/cleanup_test_data.py

    Actually delete (still requires typing DELETE to proceed):
        uv run python scripts/cleanup_test_data.py --confirm
"""

import argparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.database.models.tender import TenderORM


TEST_PREFIX = "TEST-"


def find_test_tenders(session) -> list[TenderORM]:
    """Return all tenders whose tender_id starts with TEST-."""

    statement = (
        select(TenderORM)
        .options(selectinload(TenderORM.evaluation))
        .where(TenderORM.tender_id.like(f"{TEST_PREFIX}%"))
        .order_by(TenderORM.id)
    )

    return list(session.scalars(statement).all())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Enable deletion. Without this flag, only a dry-run "
            "report is printed and nothing is deleted."
        ),
    )
    args = parser.parse_args()

    with SessionLocal() as session:
        test_tenders = find_test_tenders(session)

        if not test_tenders:
            print(
                "No test data found (no tender_id starting with "
                f"'{TEST_PREFIX}'). Nothing to do."
            )
            return

        print(f"Found {len(test_tenders)} test tender(s):\n")

        for tender in test_tenders:
            has_evaluation = tender.evaluation is not None
            print(
                f"  id={tender.id}  "
                f"tender_id={tender.tender_id}  "
                f"title={tender.tender_title!r}  "
                f"has_evaluation={has_evaluation}"
            )

        if not args.confirm:
            print(
                f"\nDRY RUN — nothing was deleted. "
                f"Re-run with --confirm to delete these "
                f"{len(test_tenders)} tender(s) (and their "
                f"evaluations, via ON DELETE CASCADE)."
            )
            return

        print(
            f"\nAbout to permanently delete {len(test_tenders)} "
            f"tender(s) listed above, from database: "
            f"{session.bind.url.database}"
        )

        response = input(
            "Type DELETE (all caps) to proceed, anything else to "
            "abort: "
        )

        if response != "DELETE":
            print("Aborted. Nothing was deleted.")
            return

        for tender in test_tenders:
            session.delete(tender)

        session.commit()

        print(
            f"\nDeleted {len(test_tenders)} test tender(s) and "
            f"their evaluations."
        )


if __name__ == "__main__":
    main()