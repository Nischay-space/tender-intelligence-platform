from datetime import datetime
from pathlib import Path

import yaml

from tender_intelligence_platform.models.prefilter_result import (
    PreFilterResult,
)
from tender_intelligence_platform.models.tender_link import TenderLink


class LinkPreFilter:
    """
    Cheap, pre-download filter that decides whether a TenderLink is worth
    a full detail scrape.

    This intentionally works with only what's available before the
    detail page is downloaded: title, reference number, and dates.
    It reuses the same filters.yaml exclude_keywords/matching config as
    KeywordEngine so there is a single source of truth for exclusions,
    but it does NOT apply include_keywords: a title alone can't reliably
    prove a tender is relevant (see work_description-only matches), so
    doing that would risk silently dropping real tenders. Full keyword
    and eligibility evaluation still runs, unchanged, after the detail
    page is scraped.
    """

    def __init__(self, config_path: str | Path):
        self._config = self._load_config(config_path)
        self._settings = self._config["keyword_filter"]

    @staticmethod
    def _load_config(config_path: str | Path) -> dict:
        """Load keyword configuration from YAML."""

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Keyword configuration not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def should_skip(
        self,
        link: TenderLink,
        *,
        now: datetime | None = None,
    ) -> PreFilterResult:
        """Decide whether to skip this link before downloading its detail page."""

        reference_time = now if now is not None else datetime.now()

        if link.closing_date < reference_time:
            return PreFilterResult(
                should_skip=True,
                reason=(
                    "Bid submission already closed on "
                    f"{link.closing_date.isoformat()}"
                ),
            )

        if not self._settings.get("enabled", True):
            return PreFilterResult(should_skip=False)

        exclude_keywords = self._settings.get("exclude_keywords") or []

        if not exclude_keywords:
            return PreFilterResult(should_skip=False)

        matching = self._settings.get("matching", {})
        case_sensitive = matching.get("case_sensitive", False)

        title = link.title if case_sensitive else link.title.lower()

        for keyword in exclude_keywords:
            search_keyword = (
                keyword if case_sensitive else keyword.lower()
            )

            if search_keyword in title:
                return PreFilterResult(
                    should_skip=True,
                    reason=f"Title matched exclude keyword: {keyword}",
                )

        return PreFilterResult(should_skip=False)