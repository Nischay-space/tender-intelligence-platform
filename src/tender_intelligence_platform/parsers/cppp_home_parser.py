from datetime import datetime

from bs4 import BeautifulSoup

from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.parsers.base_parser import BaseParser


class CPPPHomeParser(BaseParser):
    HTML_PARSER = "html.parser"
    BASE_URL = "https://eprocure.gov.in"

    def parse(self, raw_data: str) -> list[TenderLink]:
        soup = BeautifulSoup(raw_data, self.HTML_PARSER)

        table = soup.find("table", id="activeTenders")

        if table is None:
            return []

        tenders: list[TenderLink] = []

        rows = table.find_all("tr")

        for row in rows:
            tender = self._parse_row(row)

            if tender is not None:
                tenders.append(tender)

        return tenders

    def _parse_row(self, row) -> TenderLink | None:
        cells = row.find_all("td")

        if len(cells) != 4:
            return None

        link = cells[0].find("a")

        if link is None:
            return None

        href = link.get("href")

        if href is None:
            return None

        return TenderLink(
            title=link.get_text(strip=True),
            reference_number=cells[1].get_text(strip=True),
            detail_url=self.BASE_URL + href,
            closing_date=self._parse_datetime(
                cells[2].get_text(strip=True)
            ),
            opening_date=self._parse_datetime(
                cells[3].get_text(strip=True)
            ),
        )

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        return datetime.strptime(
            value,
            "%d-%b-%Y %I:%M %p",
        )