import pandas as pd

from dutch_news_scraper.utils.date_prep import get_date_list

from typing import List, Union

from dutch_news_scraper.scraper import BaseScraper, Result


class NosScraper(BaseScraper):
    def __init__(self):
        super.__init__()
        self.name = "nos"
        self.base_url = "https://nos.nl/nieuws/archief/"
        self.base_url_child = "https://nos.nl"

    def identify_parent_links(self, date_start: str = "20230101", date_end: str = "20230103",
                              input_format: str = "%Y-%m-%d", output_format: str = "%Y-%m-%d") -> List[str]:
        dates = get_date_list(date_start, date_end, input_format, output_format)
        all_parents = [f"{self.base_url}{date}" for date in dates]
        return all_parents

    def scrape_one_parent(self, url: str) -> List[str]:
        soup = self._prepare_soup(url)
        a_href = soup.find_all("a", {"class": "link-block"})
        child_links = [a.get("href") for a in a_href]
        return child_links

    def scrape_one_child(self, url: str) -> Result:
        soup = self._prepare_soup(url)
        title = soup.find("h1").getText()
        body = [i.getText() for i in soup.find_all("p")]
        date = "ddd"
        result = Result(title, body, date, url)
        return result

    def run(
            self, date_start: str = "20230101", date_end: str = "20230103",
            input_format: str = "%Y-%m-%d", output_format: str = "%Y-%m-%d", to_df: bool = True
    ) -> Union[pd.DataFrame, List[Result]]:
        all_parents = self.identify_parent_links(date_start, date_end, input_format, output_format)
        all_childs = self.scrape_parents(all_parents)
        results = self.scrape_childs(all_childs)
        if to_df:
            df_result = self.to_df(results)
            return df_result
        else:
            return results


if __name__ == "__main__":
    scraper = NosScraper()

