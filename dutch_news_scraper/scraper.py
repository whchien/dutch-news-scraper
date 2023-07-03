import multiprocessing as mp
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Union

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


class BaseScraper(ABC):
    def __init__(self):
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
            warnings.warn(f"Page not found. HTTP {res.status_code}: {url}", UserWarning)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup

    def to_df(self, results: List[Result]) -> pd.DataFrame:
        for k, _ in self.result_dict.items():
            self.result_dict[k] = [result.__getattribute__(k) for result in results]

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
        all_child_links = [x for c in all_child_links for x in c]
        self.child_links = all_child_links
        return all_child_links

    @abstractmethod
    def identify_parent_links(self):
        pass

    @abstractmethod
    def run(self):
        pass
