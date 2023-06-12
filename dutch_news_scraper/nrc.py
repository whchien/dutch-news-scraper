from typing import List

from dutch_news_scraper.scraper import BaseScraper, Result


class NrcScraper(BaseScraper):
    def __init__(self):
        super.__init__()
        self.name = "techzine"

    def identify_parent_links(self, n_pages: int = 3) -> List[str]:
        types = [
            "analytics",
            "topstories",
            "applications",
            "collaboration",
            "privacy-compliance",
            "security",
            "devices",
            "devops",
            "infrastructure",
            "data-management",
            "infrastructure",
        ]
        all_parents = [
            f"https://www.techzine.nl/{type}/page/{i}"
            for i in range(1, n_pages + 1)
            for type in types
        ]
        return all_parents

    def scrape_one_parent(self, url: str) -> List[str]:
        soup = self._prepare_soup(url)
        child_links = [
            s.select("a")[0].get_attribute_list("href")[0]
            for s in soup.select("#main .category-analytics")
        ]
        return child_links

    def scrape_one_child(self, url: str) -> Result:
        soup = self._prepare_soup(url)
        title = soup.select(".entry-header .entry-title")[0].text
        body = [i.text for i in soup.select("#main p , .entry-header .entry-title")]
        body = " ".join(body)
        date = soup.select(".published")[0].text
        result = Result(title, body, date, url)
        return result
