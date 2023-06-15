from dutch_news_scraper.nu import NuScraper
from dutch_news_scraper.techzine import TechzineScraper


class NewsScrpaer:

    def __init__(self, name: str, **kwargs):
        scrapers = {"techzine": TechzineScraper,
                    "nu": NuScraper}
        self.name = name
        self.scraper = scrapers.get(name)

    def run(self, **kwargs):
        return self.scraper(**kwargs)


if __name__ == "__main__":
    scraper = NewsScrpaer(name="nu")
    scraper.run()