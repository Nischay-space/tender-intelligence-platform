from abc import ABC, abstractmethod

from tender_intelligence_platform.models.tender import Tender


class BaseParser(ABC):

    @abstractmethod
    def parse(self, raw_data) -> Tender:
        """
        Parse raw tender data into a Tender model.
        """
        pass