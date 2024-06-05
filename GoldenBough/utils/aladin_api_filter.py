import os
import aiohttp
import asyncio
import pandas as pd
from konlpy.tag import Okt
from collections import Counter
import Config

from aladin_cache import WeeklyCacheManager

cache_manager = WeeklyCacheManager(cache_dir=os.path.join(Config.base_dir, "GoldenBough/cache"))

class AladinItemListFinder:
    def __init__(self):
        self.config_manager = Config.configManager
        self.url_base = "http://www.aladin.co.kr/ttb/api/ItemList.aspx"
        self.ttb_key = self.config_manager.config.secret_key
        self.query_type = "BlogBest"
        self.version = "20131101"
        self.search_target = "Book"
        self.max_results = 10
        self.start = 1
        self.is_json = True
        self.will_filter_sold_out = False
        self.year = -1
        self.month = -1
        self.week = -1
        self.category_id = 0

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
            "CategoryId": self.category_id
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
        return self.url

    async def request_data(self) -> pd.DataFrame:
        self.combine_settings()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    
                    # raise exception when json contains ERROR MESSAGE.
                    if "errorMessage" in response_json:
                        raise ApiRuntimeException(response_json["errorMessage"])
                    
                    # print entire json response to debug
                    print(response_json)
                    
                    # books are in item list so
                    data = pd.DataFrame(response_json.get('item', []))
                    return await self.exclude_light_novel(data)
                else:
                    response.raise_for_status()

    async def exclude_light_novel(self, data: pd.DataFrame) -> pd.DataFrame:
        # Light Novel is not a literature!
        if 'categoryName' in data.columns:
            await cache_manager.save_weekly_data(data, self.year, self.month, self.week)
            return data[~data['categoryName'].str.contains("라이트 노벨")]
        return data


class ApiRuntimeException(Exception):
    pass


def process_description(description: str) -> pd.DataFrame:
    stopwords = [
        '이', '있', '하', '것', '들', '그', '되', '수', '보', '않', '없', '나', '사람', '주', '아니', '등', 
        '같', '우리', '때', '년', '가', '한', '지', '대하', '오', '말', '일', '그렇', '위하', '그리고', 
        '하지만', '그러나', '또한', '더욱이', '게다가', '때문에', '이어서', '또', '그런데', '따라서', 
        '그래서', '여기서', '저기서', '먼저', '바로', '다시', '결국', '즉', '그래도'
    ]
    stopwords = list(set(stopwords))
    okt = Okt()

    # 명사 추출
    nouns = okt.nouns(description)
    
    # 불용어 제거
    filtered_nouns = [noun for noun in nouns if noun not in stopwords]
    
    # 단어 빈도 계산
    word_freq = Counter(filtered_nouns)
    most_common_words = word_freq.most_common()
    
    data = {
        'Word': [word for word, freq in most_common_words],
        'Frequency': [freq for word, freq in most_common_words]
    }
    df = pd.DataFrame(data)
    
    return df

def save_to_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False, encoding='utf-8-sig')

async def filter_books_by_specific_category(books: pd.DataFrame, category_keyword: str) -> pd.DataFrame:
    if 'categoryName' in books.columns:
        filtered_books = books[books['categoryName'].str.contains(category_keyword)]
        return filtered_books
    return books

async def filter_and_save_books(category_keyword: str, filename: str):
    finder = AladinItemListFinder()
    finder.filter_sold_out(True).specific_date(2024, 5, 3).query("Bestseller").start_page(
        1).result_per_page(100).search_category(1)
    data = await finder.request_data()

    filtered_books = await filter_books_by_specific_category(data, category_keyword)

    if filtered_books.empty:
        print(f"해당 카테고리에 대한 책이 없습니다: {category_keyword}")
        return

    descriptions = ' '.join(filtered_books['description'].dropna().tolist())
    processed_df = process_description(descriptions)
    
    save_to_csv(processed_df, filename)
    
    print(f"CSV 파일 저장 완료: {filename}")

async def main():
    categories = ['로맨스', 'SF', '판타지', '역사']
    for category in categories:
        await filter_and_save_books(category, f'filtered_books_{category}.csv')

if __name__ == "__main__":
    asyncio.run(main())