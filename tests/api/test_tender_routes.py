from uuid import uuid4

from fastapi.testclient import TestClient

from tender_intelligence_platform.api.app import app
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "tender-intelligence-platform",
    }


def test_list_tenders_returns_200_and_a_list(db_session, make_tender):
    repository = TenderRepository(db_session)
    tender = make_tender()

    repository.create(tender)
    db_session.commit()

    response = client.get("/api/v1/tenders", params={"limit": 100})

    assert response.status_code == 200

    body = response.json()
    assert isinstance(body, list)
    assert any(
        item["tender_id"] == tender.tender_id for item in body
    )


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
    assert len(response.json()) <= 2


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