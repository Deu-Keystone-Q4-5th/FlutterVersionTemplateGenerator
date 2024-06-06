import asyncio
import os

import aiohttp
import pandas as pd

from utils import datetimeutils, Config, npl3
from utils.aladin_cache import WeeklyCacheManager
from utils.requestAPI import apiImporter

cache_manager = WeeklyCacheManager(cache_dir=os.path.join(Config.base_dir, "cache"))


class AladinItemListFinder (apiImporter):
    def __init__(self):
        self.config_manager = Config.configManager
        self.url_base = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
        self.ttb_key = self.config_manager.config.secret_key
        self.query_type = "Bestseller"
        self.version = "20131101"
        self.search_target = "Book"
        self.max_results = 50
        self.start = 1
        self.cover_size = "Big"
        self.is_json = True
        self.will_filter_sold_out = False
        self.year, self.month, self.week = datetimeutils.get_month_week()
        self.category_id = 1

    def filter_sold_out(self, value: bool):
        self.will_filter_sold_out = value
        return self

    def specific_date(self, year: int, month: int, week: int):
        self.year = year
        self.month = month
        self.week = week
        return self

    def query(self, query: str):
        self.query_type = query
        return self

    def start_page(self, start: int):
        self.start = start
        return self

    def search_category(self, category_id: int):
        self.category_id = category_id
        return self

    def result_per_page(self, max_results: int):
        self.max_results = max_results
        return self

    def combine_settings(self):
        output_format = "js" if self.is_json else "xml"
        args = {
            "ttbkey": self.ttb_key,
            "QueryType": self.query_type,
            "Version": self.version,
            "SearchTarget": self.search_target,
            "MaxResults": self.max_results,
            "start": self.start,
            "Output": output_format,
            "CategoryId": self.category_id,
            "Cover": self.cover_size
        }

        if self.year != -1:
            args["Year"] = self.year
        if self.month != -1:
            args["Month"] = self.month
        if self.week != -1:
            args["Week"] = self.week
        if self.will_filter_sold_out:
            args["outStockfilter"] = 1

        self.url = f"{self.url_base}?" + "&".join([f"{k}={v}" for k, v in args.items()])
        print(self.url)
        return self.url

    async def request(self) -> pd.DataFrame:
        self.combine_settings()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    response_json = await response.json()

                    # raise exception when json contains ERROR MESSAGE.
                    if "errorMessage" in response_json:
                        raise ApiRuntimeException(response_json["errorMessage"] + Config.config_folder)
                    print(response_json)
                    # books are in item list so
                    page = response_json["startIndex"]
                    data = pd.DataFrame(response_json.get('item', []))
                    print("got items")
                    return await self.filter_data(data, page)
                else:
                    response.raise_for_status()

    async def filter_data(self, data: pd.DataFrame, page: int) -> pd.DataFrame:
        print("filtering...")
        # Light Novel is not a literature!
        if 'categoryName' in data.columns:
            data = await npl3.process_text(data)
            data = data[~data['categoryName'].str.contains("라이트 노벨")]
            data['stockStatus'] = data["stockStatus"].replace('', "구매 가능")
            await cache_manager.save_weekly_data(data, self.year, self.month, self.week, page)
            return data

        return data


class ApiRuntimeException(Exception):
    pass


async def test():
    finder = AladinItemListFinder()
    finder.filter_sold_out(True).specific_date(2024, 5, 3).query("Bestseller").start_page(
        1).result_per_page(100).search_category(1)
    data = finder.request()
    print("test")
    titles = await data
    titles.to_csv("books.csv", index=False, encoding="utf-8-sig")
    json = titles.to_json(orient="index", index=True, force_ascii=False, indent=4)
    print(json)


if __name__ == "__main__":
    asyncio.run(test())
