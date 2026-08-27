from datetime import datetime, timedelta
from pathlib import Path

from tender_intelligence_platform.engines.link_prefilter import (
    LinkPreFilter,
)
from tender_intelligence_platform.models.tender_link import TenderLink


NOW = datetime(2026, 8, 25, 12, 0, 0)


def make_link(
    title: str = "Construction of District Office Building",
    closing_date: datetime | None = None,
) -> TenderLink:
    return TenderLink(
        title=title,
        reference_number="REF-001",
        detail_url="https://example.com/tender/1",
        closing_date=closing_date or (NOW + timedelta(days=5)),
        opening_date=NOW + timedelta(days=6),
    )


def create_config(
    tmp_path: Path,
    *,
    exclude_keywords=None,
    enabled=True,
    case_sensitive=False,
) -> Path:
    exclude_keywords = (
        exclude_keywords
        if exclude_keywords is not None
        else ["highway", "road construction", "bridge construction"]
    )

    config = f"""
keyword_filter:
  enabled: {str(enabled).lower()}

  include_keywords:
    - "construction"

  exclude_keywords:
"""

    for keyword in exclude_keywords:
        config += f'    - "{keyword}"\n'

    config += f"""
  search_fields:
    - tender_title

  matching:
    case_sensitive: {str(case_sensitive).lower()}
    partial_match: true

  minimum_matches: 1
"""

    config_path = tmp_path / "filters.yaml"
    config_path.write_text(config)

    return config_path


def test_skips_link_with_closed_bid_submission(tmp_path):
    config_path = create_config(tmp_path)
    prefilter = LinkPreFilter(config_path)

    link = make_link(closing_date=NOW - timedelta(days=1))

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is True
    assert "closed" in result.reason.lower()


def test_does_not_skip_link_with_open_bid_submission(tmp_path):
    config_path = create_config(tmp_path)
    prefilter = LinkPreFilter(config_path)

    link = make_link(closing_date=NOW + timedelta(days=5))

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is False


def test_skips_link_whose_title_matches_exclude_keyword(tmp_path):
    config_path = create_config(tmp_path)
    prefilter = LinkPreFilter(config_path)

    link = make_link(title="Highway Widening Project Phase 2")

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is True
    assert "exclude keyword" in result.reason.lower()


def test_does_not_skip_title_missing_include_keyword(tmp_path):
    """
    A title that doesn't mention any include_keyword must NOT be skipped —
    relevance can only be confirmed after the full detail page (title +
    work_description + category + organization) is evaluated.
    """

    config_path = create_config(tmp_path)
    prefilter = LinkPreFilter(config_path)

    link = make_link(
        title="Repair Work at District Hospital Annexe"
    )

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is False


def test_exclude_check_is_case_insensitive_by_default(tmp_path):
    config_path = create_config(tmp_path)
    prefilter = LinkPreFilter(config_path)

    link = make_link(title="HIGHWAY Expansion Project")

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is True


def test_disabled_keyword_filter_skips_only_on_closed_dates(tmp_path):
    config_path = create_config(tmp_path, enabled=False)
    prefilter = LinkPreFilter(config_path)

    link = make_link(title="Highway Widening Project Phase 2")

    result = prefilter.should_skip(link, now=NOW)

    assert result.should_skip is False


def test_missing_config_file_raises_file_not_found(tmp_path):
    missing_path = tmp_path / "does_not_exist.yaml"

    try:
        LinkPreFilter(missing_path)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass