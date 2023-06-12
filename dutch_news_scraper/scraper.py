import multiprocessing as mp
from typing import Dict, Union, List
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import process_map


@dataclass
class Result:
    title: Union[str, None] = None
    body: Union[str, None] = None
    date: Union[str, None] = None
    url: Union[str, None] = None


class BaseScraper(object):
    def __init__(self, name: str = "generic"):
        self.name = name
        self.pools = mp.cpu_count()
        self.result_dict: Dict[str, list] = {k: [] for k in ["title", "date", "body", "url"]}
        self.result_df = None
        self.base_url = "https://www.example.nl/"
        self.parent_links: List[str] = []
        self.child_links: List[str] = []

    @staticmethod
    def _prepare_soup(url: str, headers: Union[Dict[str, str], None] = None) -> BeautifulSoup:
        res = requests.get(url, headers=headers)
        if res.status_code in (403, 404, 410):
            raise Exception(f"Page not found. HTTP {res.status_code}: {url}")
        soup = BeautifulSoup(res.text, "lxml")
        return soup

    def to_df(self, results: List[Result]) -> pd.DataFrame:
        for k, _ in self.result_dict.items():
            self.result_dict[k] = [result.k for result in results]  # type: ignore

        result_df = pd.DataFrame(self.result_dict)
        return result_df

    def scrape_one_child(self, url: str) -> Result:
        soup = self._prepare_soup(url)
        title = soup.select(".title")[0].text
        body = soup.select(".body")[0].text
        date = soup.select(".date")[0].text
        result = Result(title, body, date, url)
        return result

    def scrape_childs(self, links: List[str]) -> List[Result]:
        results = process_map(self.scrape_one_child, links, max_workers=self.pools)
        return results

    def scrape_one_parent(self, url: str) -> List[str]:
        soup = self._prepare_soup(url)
        links = soup.select(".parent_links")
        child_links = [link.get_attribute_list("href")[0] for link in links]
        return child_links

    def scrape_parents(self, parent_links: List[str]) -> List[str]:
        all_child_links = process_map(
            self.scrape_one_parent, parent_links, max_workers=self.pools
        )
        self.child_links = all_child_links
        return all_child_links

    def identify_parent_links(self, n_pages: int = 3) -> List[str]:
        all_parents_links = [f"{self.base_url}/{i}" for i in range(1, n_pages)]
        self.parent_links = all_parents_links
        return all_parents_links

    def run(
        self, n_pages: int = 3, to_df: bool = True
    ) -> Union[pd.DataFrame, List[Result]]:
        all_parents = self.identify_parent_links(n_pages)
        all_childs = self.scrape_parents(all_parents)
        results = self.scrape_childs(all_childs)
        if to_df:
            df_result = self.to_df(results)
            return df_result
        else:
            return results