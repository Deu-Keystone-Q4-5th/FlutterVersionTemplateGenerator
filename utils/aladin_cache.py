import os
from io import StringIO

import pandas as pd
from pathlib import Path
import aiofiles
import asyncio
import re

from utils import Config

path = "cache"


class WeeklyCacheManager:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_week_string(self, year: int, month: int, week: int, page: int) -> str:
        return f"{year}_{month:02d}_week{week}_page{page}"

    async def save_weekly_data(self, data: pd.DataFrame, year: int, month: int, week: int, page: int = 1):
        week_string = self.get_week_string(year, month, week, page)
        file_path = self.cache_dir / f"titles_{week_string}.csv"
        async with aiofiles.open(file_path, 'w', encoding="utf-8-sig") as f:
            await f.write(data.to_csv(index=False))
        print(f"Data saved to {file_path}")

    async def load_weekly_data(self, year: int, month: int, week: int, page: int = 1) -> pd.DataFrame:
        week_string = self.get_week_string(year, month, week, page)
        file_path = self.cache_dir / f"titles_{week_string}.csv"
        if file_path.exists():
            async with aiofiles.open(file_path, 'r', encoding="utf-8-sig") as f:
                content = await f.read()

            data = pd.read_csv(StringIO(content), dtype=str)
            print(f"Data loaded from {file_path}")
            return data
        else:
            print(f"No data found for {week_string}")
            return pd.DataFrame()

    def is_week_cached(self, year: int, month: int, week: int, page: int = 1) -> bool:
        week_string = self.get_week_string(year, month, week, page)
        file_path = self.cache_dir / f"titles_{week_string}.csv"
        return file_path.exists()

    def get_cached_weeks(self):
        cached_files = list(self.cache_dir.glob("titles_*.csv"))
        cached_weeks = []

        for file_path in cached_files:
            match = re.match(r"titles_(\d{4})_(\d{2})_week(\d+)\.csv", file_path.name)
            if match:
                year, month, week = map(int, match.groups())
                cached_weeks.append((year, month, week))

        return cached_weeks


async def test():
    from utils.aladin_api_helper import AladinItemListFinder
    finder = AladinItemListFinder()
    cache_manager = WeeklyCacheManager(cache_dir=os.path.join(Config.base_dir, "cache"))

    year = 2024
    month = 5
    week = 3

    if cache_manager.is_week_cached(year, month, week, 1):
        data = await cache_manager.load_weekly_data(year, month, week, 1)
    else:
        finder.filter_sold_out(True).specific_date(year, month, week).query("Bestseller").start_page(1).result_per_page(
            100).search_category(1)
        data = await finder.request()
        await cache_manager.save_weekly_data(data, year, month, week)

    # Use the data
    print(data)

    cached_weeks = cache_manager.get_cached_weeks()
    print("Cached weeks:", cached_weeks)


if __name__ == "__main__":
    asyncio.run(test())
