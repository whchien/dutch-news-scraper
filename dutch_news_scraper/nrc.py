from typing import List, Union

import pandas as pd

from dutch_news_scraper.scraper import BaseScraper, Result


class NrcScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "nrc"
        self.base_url = ""

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
        body_list = [i.text for i in soup.select("#main p , .entry-header .entry-title")]
        body = " ".join(body_list)
        date = soup.select(".published")[0].text
        result = Result(title, body, date, url)
        return result

    def run(
        self, n_pages: int = 3, to_df: bool = True) -> Union[pd.DataFrame, List[Result]]:
        all_parents = self.identify_parent_links(n_pages)
        all_childs = self.scrape_parents(all_parents)
        results = self.scrape_childs(all_childs)
        if to_df:
            df_result = self.to_df(results)
            return df_result
        else:
            return results

