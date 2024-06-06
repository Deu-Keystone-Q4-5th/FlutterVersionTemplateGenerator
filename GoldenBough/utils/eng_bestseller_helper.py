import asyncio

import aiohttp
import pandas as pd

import Config
from GoldenBough.utils.requestAPI import apiImporter
from aladin_api_helper import ApiRuntimeException


class BestsellerAPI (apiImporter):
    def __init__(self):
        self.url = "https://api.nytimes.com/svc/books/v3/lists"
        self.date = "current"
        self.category = "hardcover-fiction.json"
        self.api_key = Config.configManager.config.eng_secret_key

    async def request(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.url}/{self.date}/{self.category}?api-key={self.api_key}") as response:
                if response.status == 200:
                    response_json = await response.json()

                    if "fault" in response_json:
                        raise ApiRuntimeException(response_json["fault"]["faultstring"])

                    if response_json["status"] == "ERROR":
                        raise ApiRuntimeException(response_json["errors"][0])

                    return await self.toDataFrame(response_json)

                else:
                    response.raise_for_status()

    async def toDataFrame(self, response_json):
        return pd.DataFrame(response_json["results"]["books"])



async def test():
    api = BestsellerAPI()
    data = await api.request()
    print(data)
    print(data.columns)


if __name__ == "__main__":
    asyncio.run(test())
