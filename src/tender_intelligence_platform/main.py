from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper


def main() -> None:
    client = HTTPClient()

    try:
        scraper = CPPPScraper(client)

        tenders = scraper.scrape()
        print(f"\nFound {len(tenders)} tenders\n")

        for tender in tenders:
            print("-" * 80)
            print(f"Title      : {tender.title}")
            print(f"Reference  : {tender.reference_number}")
            print(f"Closing    : {tender.closing_date}")
            print(f"Opening    : {tender.opening_date}")
            print(f"URL        : {tender.detail_url}")

    finally:
        client.close()


if __name__ == "__main__":
    main()