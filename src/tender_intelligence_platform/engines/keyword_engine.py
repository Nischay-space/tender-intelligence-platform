from pathlib import Path

import yaml

from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.tender import Tender


class KeywordEngine:
    """Configuration-driven tender relevance engine."""

    def __init__(
        self,
        config_path: str | Path,
    ):
        self._config = self._load_config(
            config_path
        )

        self._settings = self._config[
            "keyword_filter"
        ]

    @staticmethod
    def _load_config(
        config_path: str | Path,
    ) -> dict:
        """Load keyword configuration from YAML."""

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Keyword configuration not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return yaml.safe_load(file)

    def evaluate(
        self,
        tender: Tender,
    ) -> FilterResult:
        """Evaluate tender relevance."""

        if not self._settings.get(
            "enabled",
            True,
        ):
            return FilterResult(
                is_relevant=True,
                reasons=[
                    "Keyword filtering is disabled"
                ],
            )

        text = self._build_search_text(
            tender
        )

        include_keywords = self._settings.get(
    "include_keywords"
) or []

        exclude_keywords = self._settings.get(
    "exclude_keywords"
) or []

        matched_keywords = self._find_matches(
            text,
            include_keywords,
        )

        excluded_keywords = self._find_matches(
            text,
            exclude_keywords,
        )

        minimum_matches = self._get_minimum_matches()

        is_relevant = (
            len(matched_keywords)
            >= minimum_matches
            and len(excluded_keywords) == 0
        )

        reasons = []

        if matched_keywords:
            reasons.append(
                "Matched keywords: "
                + ", ".join(matched_keywords)
            )

        if excluded_keywords:
            reasons.append(
                "Excluded keywords: "
                + ", ".join(excluded_keywords)
            )

        if not reasons:
            reasons.append(
                "No configured keywords matched"
            )

        return FilterResult(
            is_relevant=is_relevant,
            matched_keywords=matched_keywords,
            excluded_keywords=excluded_keywords,
            reasons=reasons,
        )

    def _build_search_text(
        self,
        tender: Tender,
    ) -> str:
        """Build searchable text from configured fields."""

        fields = self._settings.get(
            "search_fields",
            [],
        )

        values = []

        for field_name in fields:
            value = getattr(
                tender,
                field_name,
                None,
            )

            if value is not None:
                values.append(str(value))

        return " ".join(values)

    def _find_matches(
        self,
        text: str,
        keywords: list[str],
    ) -> list[str]:
        """Find configured keywords in text."""

        matching = self._settings.get(
            "matching",
            {},
        )

        case_sensitive = matching.get(
            "case_sensitive",
            False,
        )

        partial_match = matching.get(
            "partial_match",
            True,
        )

        if not case_sensitive:
            text = text.lower()

        matches = []

        for keyword in keywords:
            search_keyword = keyword

            if not case_sensitive:
                search_keyword = keyword.lower()

            if partial_match:
                found = (
                    search_keyword in text
                )
            else:
                found = self._exact_word_match(
                    text,
                    search_keyword,
                )

            if found:
                matches.append(keyword)

        return matches

    @staticmethod
    def _exact_word_match(
        text: str,
        keyword: str,
    ) -> bool:
        """Perform simple whole-word matching."""

        import re

        pattern = (
            rf"\b{re.escape(keyword)}\b"
        )

        return re.search(
            pattern,
            text,
        ) is not None
    def _get_minimum_matches(self) -> int:
        """Return a validated minimum keyword match count."""

        value = self._settings.get(
            "minimum_matches",
            1,
        )

        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "minimum_matches must be a positive integer"
            ) from exc

        if value < 1:
            raise ValueError(
                "minimum_matches must be at least 1"
            )

        return value