import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import time
import pendulum
import datetime
import random

http_get_interval = random.randint(1, 5)


def extract(
        tree: HTMLParser,
        selector: str,
        option: str,
        result: str = "",
):
    element = tree.css_first(selector)
    if element is not None:
        match option:
            case "text":
                return element.text(strip=True)
            case "attrs":
                return element.attributes
            case _:
                return element
    else:
        return result


@dataclass
class AisekiyaData:
    store_name: str
    address: str
    mens_current: int
    mens_max: int
    mens_pct: float
    womens_current: int
    womens_max: int
    womens_pct: float
    mens_womens_pct: float  # mens / womens: if more than 1.0 then mens are more than womens
    datetime: datetime = pendulum.now('UTC')
    # datetime: str = pendulum.now('UTC').in_timezone('Asia/Tokyo').strftime("%Y-%m-%d %H:%M:%S")


class GetStores:
    def __init__(self, url: str):
        self.url = url
        self.stores = []

    def get_stores(self) -> None:
        response = httpx.get(self.url)
        response.raise_for_status()
        tree = HTMLParser(response.text)

        links_selector = "#congestion > div.p-congestion__body.u-bgColor--grayLight > div > ul > li > a"
        self.stores = [node.attributes["href"].replace(" ", "").replace("\n", "") for node in tree.css(links_selector)]


class GetStoreData:
    def __init__(self, store_urls: list):
        self.store_urls = store_urls
        self.all_store_data = []

    def get_store_data(self, store_url: str) -> None:
        response = httpx.get(store_url)
        response.raise_for_status()
        tree = HTMLParser(response.text)

        store_name_selector = "body > div.l-default > div.l-contents > main > div > h1"
        address_selector = "body > div.l-default > div.l-contents > main > section:nth-child(5) > div > div > dl:nth-child(3) > dd"
        mens_current_selector = ("body > div > div > main > "
                                 "section > div > div > div > "
                                 "dl:nth-child(1) > dd > span:nth-child(1)")
        mens_max_selector = ("body > div.l-default > div.l-contents > main > "
                             "section > div > div > div > dl:nth-child(1) > dd > "
                             "span:nth-child(3)")
        womens_current_selector = ("body > div.l-default > div.l-contents > main > "
                                   "section > div > div > div > dl:nth-child(3) > dd > "
                                   "span:nth-child(1)")
        womens_max_selector = ("body > div.l-default > div.l-contents > main > "
                               "section > div > div > div > dl:nth-child(3) > dd > "
                               "span:nth-child(3)")

        mens_current = int(extract(tree, mens_current_selector, "text", "0"))
        womens_current = int(extract(tree, womens_current_selector, "text", "0"))
        mens_max = int(extract(tree, mens_max_selector, "text"))
        womens_max = int(tree.css_first(womens_max_selector).text())

        if womens_current != 0:
            mens_womens_pct = round(mens_current / womens_current, 2)
        else:
            mens_womens_pct = 0.0

        store_data = AisekiyaData(
            store_name=extract(tree, store_name_selector, "text"),
            address=extract(tree, address_selector, "text"),
            mens_current=mens_current,
            mens_max=mens_max,
            mens_pct=round(mens_current / mens_max, 2),
            womens_current=womens_current,
            womens_max=womens_max,
            womens_pct=round(womens_current / womens_max, 2),
            mens_womens_pct=mens_womens_pct,
        )
        self.all_store_data.append(asdict(store_data))

    def iterable(self):
        for store_url in self.store_urls:
            time.sleep(http_get_interval)
            self.get_store_data(store_url)


if __name__ == "__main__":
    ...
    # url = "https://aiseki-ya.com/"
    # get_stores = GetStores(url)
    # get_stores.get_stores()
    #
    # get_store_data = GetStoreData(get_stores.stores)
    # get_store_data.iterable()
    #
    # data_framing.generating_df(get_store_data.all_store_data)
# TODO: Store data in a database
# TODO: Schedule to run every 30 minutes from 5pm to 5am -> Github Actions
