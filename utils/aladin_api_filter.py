import asyncio
import pandas as pd
from konlpy.tag import Kkma
from collections import Counter
from utils.aladin_api_helper import AladinItemListFinder


def process_description(description: str) -> pd.DataFrame:
    stopwords = [
        '이', '있', '하', '것', '들', '그', '되', '수', '보', '않', '없', '나', '사람', '주', '아니', '등',
        '같', '우리', '때', '년', '가', '한', '지', '대하', '오', '말', '일', '그렇', '위하', '그리고',
        '하지만', '그러나', '또한', '더욱이', '게다가', '때문에', '이어서', '또', '그런데', '따라서',
        '그래서', '여기서', '저기서', '먼저', '바로', '다시', '결국', '즉', '그래도'
    ]
    stopwords = list(set(stopwords))
    okt = Kkma()

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
    data = await finder.request()

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
