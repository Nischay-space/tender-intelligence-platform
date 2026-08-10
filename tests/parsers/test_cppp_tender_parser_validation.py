import pytest

from tender_intelligence_platform.parsers.cppp_tender_parser import (
    CPPPTenderParser,
)


def test_missing_tender_id_is_rejected():
    parser = CPPPTenderParser()

    details = {
        "Title": "Example Tender",
    }

    with pytest.raises(
        ValueError,
        match="Required CPPP field missing: Tender ID",
    ):
        parser._build_tender(
            details=details,
            tender_url="https://example.com/tender",
        )


def test_missing_title_is_rejected():
    parser = CPPPTenderParser()

    details = {
        "Tender ID": "TEST-001",
    }

    with pytest.raises(
        ValueError,
        match="Required CPPP field missing: Title",
    ):
        parser._build_tender(
            details=details,
            tender_url="https://example.com/tender",
        )

def test_parse_amount():
    assert (
        CPPPTenderParser._parse_amount(
            "1,51,18,611"
        )
        == 15118611.0
    )


def test_parse_amount_with_currency_symbol():
    assert (
        CPPPTenderParser._parse_amount(
            "₹ 10,000"
        )
        == 10000.0
    )


def test_parse_amount_missing_value():
    assert (
        CPPPTenderParser._parse_amount(None)
        is None
    )


def test_parse_boolean_yes():
    assert (
        CPPPTenderParser._parse_bool("Yes")
        is True
    )


def test_parse_boolean_no():
    assert (
        CPPPTenderParser._parse_bool("No")
        is False
    )


def test_parse_boolean_missing_value():
    assert (
        CPPPTenderParser._parse_bool(None)
        is None
    )