from uuid import uuid4

from fastapi.testclient import TestClient

from tender_intelligence_platform.api.app import app
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "tender-intelligence-platform",
    }


def test_list_tenders_returns_200_and_items(db_session, make_tender):
    repository = TenderRepository(db_session)
    tender = make_tender()

    repository.create(tender)
    db_session.commit()

    response = client.get("/api/v1/tenders", params={"limit": 100})

    assert response.status_code == 200

    body = response.json()
    assert "items" in body
    assert "total" in body
    assert isinstance(body["items"], list)
    assert any(
        item["tender_id"] == tender.tender_id
        for item in body["items"]
    )
    assert body["total"] >= 1


def test_list_tenders_respects_limit(db_session, make_tender):
    repository = TenderRepository(db_session)

    for _ in range(3):
        repository.create(make_tender())
    db_session.commit()

    response = client.get(
        "/api/v1/tenders",
        params={"skip": 0, "limit": 2},
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body["items"]) <= 2
    assert body["limit"] == 2
    assert body["skip"] == 0


def test_list_tenders_filters_by_final_status(
    db_session,
    make_tender,
    make_evaluation_result,
):
    tender_repository = TenderRepository(db_session)
    evaluation_repository = TenderEvaluationRepository(
        db_session
    )

    tender_orm = tender_repository.create(make_tender())
    db_session.commit()

    evaluation_repository.upsert(
        tender_orm.id,
        make_evaluation_result(),
    )
    db_session.commit()

    response = client.get(
        "/api/v1/tenders",
        params={
            "final_status": "QUALIFIED",
            "limit": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert any(
        item["tender_id"] == tender_orm.tender_id
        for item in body["items"]
    )
    assert all(
        item["evaluation"]["final_status"] == "QUALIFIED"
        for item in body["items"]
    )


def test_list_tenders_rejects_invalid_sort_by(db_session):
    response = client.get(
        "/api/v1/tenders",
        params={"sort_by": "not_a_real_field"},
    )

    assert response.status_code == 422


def test_get_tender_by_id_returns_200(db_session, make_tender):
    repository = TenderRepository(db_session)
    tender = make_tender()

    repository.create(tender)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenders/{tender.tender_id}"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["tender_id"] == tender.tender_id
    assert body["tender_title"] == tender.tender_title


def test_get_tender_by_id_404_when_missing():
    missing_id = f"MISSING-{uuid4().hex[:8]}"

    response = client.get(
        f"/api/v1/tenders/{missing_id}"
    )

    assert response.status_code == 404


def test_get_tender_evaluation_returns_evaluation(
    db_session,
    make_tender,
    make_evaluation_result,
):
    tender_repository = TenderRepository(db_session)
    evaluation_repository = TenderEvaluationRepository(
        db_session
    )

    tender_orm = tender_repository.create(make_tender())
    db_session.commit()

    evaluation_repository.upsert(
        tender_orm.id,
        make_evaluation_result(),
    )
    db_session.commit()

    response = client.get(
        f"/api/v1/tenders/{tender_orm.tender_id}/evaluation"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["final_status"] == "QUALIFIED"
    assert body["keyword_status"] == "RELEVANT"
    assert body["eligibility_status"] == "ELIGIBLE"


def test_get_tender_evaluation_404_when_tender_missing():
    missing_id = f"MISSING-{uuid4().hex[:8]}"

    response = client.get(
        f"/api/v1/tenders/{missing_id}/evaluation"
    )

    assert response.status_code == 404


def test_get_tender_evaluation_404_when_no_evaluation(
    db_session,
    make_tender,
):
    repository = TenderRepository(db_session)
    tender = make_tender()

    repository.create(tender)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenders/{tender.tender_id}/evaluation"
    )

    assert response.status_code == 404


def test_tender_stats_returns_counts(db_session, make_tender):
    tender_repository = TenderRepository(db_session)
    evaluation_repository = TenderEvaluationRepository(db_session)

    def seed(status: str, keyword_status: str, eligibility_status: str):
        tender_orm = tender_repository.create(make_tender())
        db_session.flush()

        evaluation_repository.upsert(
            tender_orm.id,
            EvaluationResult(
                status=status,
                keyword_result=FilterResult(
                    is_relevant=keyword_status == "RELEVANT",
                    matched_keywords=[],
                    excluded_keywords=[],
                    reasons=[],
                ),
                eligibility_result=EligibilityResult(
                    status=eligibility_status,
                    passed_rules=[],
                    failed_rules=[],
                    unknown_rules=[],
                    reasons=[],
                ),
                reasons=[f"Final evaluation status: {status}"],
            ),
        )

    seed("QUALIFIED", "RELEVANT", "ELIGIBLE")
    seed("FILTERED_OUT", "NOT_RELEVANT", "UNKNOWN")
    seed("NOT_ELIGIBLE", "RELEVANT", "NOT_ELIGIBLE")
    seed("REVIEW_REQUIRED", "RELEVANT", "UNKNOWN")

    # one tender with no evaluation at all
    tender_repository.create(make_tender())

    db_session.commit()

    response = client.get("/api/v1/tenders/stats")

    assert response.status_code == 200

    body = response.json()
    assert body["qualified"] >= 1
    assert body["filtered_out"] >= 1
    assert body["not_eligible"] >= 1
    assert body["review_required"] >= 1
    assert body["unevaluated"] >= 1
    assert body["total"] >= 5

def test_cors_header_present_for_allowed_origin():
    response = client.get(
        "/api/v1/tenders",
        params={"limit": 1},
        headers={"Origin": "http://localhost:3000"},
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "http://localhost:3000"
    )