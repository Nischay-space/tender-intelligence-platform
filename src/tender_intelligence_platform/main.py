from http import client

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config import settings
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper


def main():

    client = HTTPClient()

    scraper = CPPPScraper(client, settings)
    
    tenders = scraper.scrape()

    print(f"Scraped {len(tenders)} tenders")

    if tenders:
        print(tenders[0])


if __name__ == "__main__":
    main()