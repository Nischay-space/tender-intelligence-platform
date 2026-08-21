from pathlib import Path

from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.models.tender import Tender


def make_tender(
    title: str = "Construction of Government Building",
) -> Tender:
    return Tender(
        tender_id="TEST-KEYWORD-001",
        tender_title=title,
        tender_url="https://example.com/tender",
        organization="Test Organization",
        category="Works",
        procurement_type="Works",
        status="Open",
        work_description="Government construction work",
    )


def create_config(
    tmp_path: Path,
    *,
    include_keywords=None,
    exclude_keywords=None,
    minimum_matches=1,
    enabled=True,
    case_sensitive=False,
    partial_match=True,
) -> Path:

    include_keywords = (
        include_keywords
        if include_keywords is not None
        else ["construction"]
    )

    exclude_keywords = (
        exclude_keywords
        if exclude_keywords is not None
        else []
    )

    config = f"""
keyword_filter:
  enabled: {str(enabled).lower()}

  search_fields:
    - tender_title
    - work_description

  include_keywords:
"""

    for keyword in include_keywords:
        config += f'    - "{keyword}"\n'

    config += """
  exclude_keywords:
"""

    for keyword in exclude_keywords:
        config += f'    - "{keyword}"\n'

    config += f"""
  minimum_matches: {minimum_matches}

  matching:
    case_sensitive: {str(case_sensitive).lower()}
    partial_match: {str(partial_match).lower()}
"""

    config_path = tmp_path / "filters.yaml"
    config_path.write_text(
        config,
        encoding="utf-8",
    )

    return config_path


def test_matching_keyword_is_relevant(tmp_path):

    config_path = create_config(
        tmp_path,
        include_keywords=["construction"],
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender()
    )

    assert result.is_relevant is True
    assert result.matched_keywords == [
        "construction"
    ]


def test_no_matching_keyword_is_filtered_out(tmp_path):

    config_path = create_config(
        tmp_path,
        include_keywords=["software"],
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender()
    )

    assert result.is_relevant is False
    assert result.matched_keywords == []


def test_excluded_keyword_filters_tender(tmp_path):

    config_path = create_config(
        tmp_path,
        include_keywords=["construction"],
        exclude_keywords=["private"],
    )

    tender = make_tender(
        "Construction of Private Building"
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(tender)

    assert result.is_relevant is False
    assert result.matched_keywords == [
        "construction"
    ]
    assert result.excluded_keywords == [
        "private"
    ]


def test_minimum_matches_is_enforced(tmp_path):

    config_path = create_config(
        tmp_path,
        include_keywords=[
            "construction",
            "government",
        ],
        minimum_matches=2,
    )

    tender = make_tender(
        "Construction of Government Building"
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(tender)

    assert result.is_relevant is True
    assert set(result.matched_keywords) == {
        "construction",
        "government",
    }


def test_minimum_matches_fails_when_not_enough_keywords(
    tmp_path,
):

    config_path = create_config(
        tmp_path,
        include_keywords=[
            "construction",
            "software",
        ],
        minimum_matches=2,
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender()
    )

    assert result.is_relevant is False
    assert result.matched_keywords == [
        "construction"
    ]


def test_matching_is_case_insensitive_by_default(
    tmp_path,
):

    config_path = create_config(
        tmp_path,
        include_keywords=["CONSTRUCTION"],
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender()
    )

    assert result.is_relevant is True
    assert result.matched_keywords == [
        "CONSTRUCTION"
    ]


def test_exact_word_matching(tmp_path):

    config_path = create_config(
        tmp_path,
        include_keywords=["construct"],
        partial_match=False,
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender(
            "Construction of Government Building"
        )
    )

    assert result.is_relevant is False


def test_disabled_keyword_filter_accepts_tender(
    tmp_path,
):

    config_path = create_config(
        tmp_path,
        include_keywords=["something_that_does_not_exist"],
        enabled=False,
    )

    engine = KeywordEngine(config_path)

    result = engine.evaluate(
        make_tender()
    )

    assert result.is_relevant is True
    assert result.reasons == [
        "Keyword filtering is disabled"
    ]