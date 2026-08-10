from bs4 import Tag


class TableParser:
    """Parse CPPP caption/value tables into dictionaries."""

    @staticmethod
    def parse(table: Tag) -> dict[str, str]:
        """
        Convert a CPPP table containing td_caption/td_field
        pairs into a dictionary.
        """

        result: dict[str, str] = {}

        captions = table.select("td.td_caption")

        for caption in captions:
            key = caption.get_text(" ", strip=True)

            if not key:
                continue

            value_cells = caption.find_next_siblings(
                "td",
                class_="td_field",
            )

            if not value_cells:
                continue

            value = value_cells[0].get_text(
                " ",
                strip=True,
            )

            result[key] = value

        return result