
import pandas as pd

from dutch_news_scraper.utils.date_prep import get_date_list

from typing import List, Union, Any

from dutch_news_scraper.scraper import BaseScraper, Result


class NosScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "nos"
        self.base_url = "https://nos.nl/nieuws/archief/"
        self.base_url_child = "https://nos.nl"

    def identify_parent_links(self, date_start: str = "2023-01-01", date_end: str = "2023-01-03",
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
        url = f"{self.base_url_child}{url}"
        soup = self._prepare_soup(url)
        title = soup.find("h1").getText()
        body = [i.getText() for i in soup.find_all("p")]
        body = " ".join(body)
        date = "ddd"
        result = Result(title, body, date, url)
        return result

    def run(
            self, date_start: str = "2023-01-01", date_end: str = "2023-01-03",
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
    result = scraper.run()
    # print(result.head())

