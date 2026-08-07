from bs4 import BeautifulSoup, Tag


class TableParser:
    """
    Utility class for extracting label-value pairs
    from HTML tables.
    """

    @staticmethod
    def parse(table: Tag) -> dict[str, str]:
        """
        Convert a table into a dictionary.

        Example:

        Tender ID  -> 2026_ARMHA_920877_1
        Tender Type -> Open Tender
        """

        data: dict[str, str] = {}

        rows = table.find_all("tr")

        for row in rows:

            cells = row.find_all("td")

            # We expect label/value pairs.
            if len(cells) < 2:
                continue

            # Iterate over pairs of cells.
            for i in range(0, len(cells) - 1, 2):

                label = cells[i].get_text(" ", strip=True)

                value = cells[i + 1].get_text(" ", strip=True)

                if label:
                    data[label] = value

        return data