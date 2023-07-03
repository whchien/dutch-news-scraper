import re
from typing import List

from dutch_news_scraper.scraper import BaseScraper, Result


class NuScraper(BaseScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "nu"
        self.base_url = "https://www.nu.nl/amsterdam/"

    def identify_parent_links(self, n_pages: int = 3) -> List[str]:
        all_parents_links = [f"{self.base_url}/{i}" for i in range(1, n_pages)]
        self.parent_links = all_parents_links
        return all_parents_links

    def run(self, start: int = 6267160, end: int = 6267165):
        # 6260000 # 2023 april
        # 6265004 # 2023 may
        # 6267165 # 2023 june
        links = [f"{self.base_url}{i}" for i in range(start, end)]
        results = self.scrape_childs(links)
        df_result = self.to_df(results)
        return df_result

    def scrape_one_child(self, url: str) -> Result:
        soup = self._prepare_soup(url)

        try:
            content = soup.find_all("script")[0].text
            heads = re.findall('(?<=headline":")(.*)(?=","dateCreated":")', content)
            body = re.findall('(?<=articleBody":")(.*)(?=","wordCount)', content)[0]
            title = heads[0].split('","url"')[0]
            date = heads[0].split('datePublished":"')[1].split("T")[0]

        except IndexError:
            title, url, date, body = None, None, None, None  # type: ignore

        result = Result(title, body, date, url)
        return result


if __name__ == "__main__":
    scraper = NuScraper()
    result = scraper.run()
    print(result.head())