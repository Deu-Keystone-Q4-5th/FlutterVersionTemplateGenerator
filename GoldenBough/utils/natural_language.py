import nltk
import pandas as pd
from konlpy.tag import Okt
from collections import Counter

nltk.download('punkt')

stopwords = [
    '이', '있', '하', '것', '들', '그', '되', '수', '보', '않', '없', '나', '사람', '주', '아니', '등', 
    '같', '우리', '때', '년', '가', '한', '지', '대하', '오', '말', '일', '그렇', '위하', '그리고', 
    '하지만', '그러나', '또한', '더욱이', '게다가', '때문에', '이어서', '또', '그런데', '따라서', 
    '그래서', '여기서', '저기서', '먼저', '바로', '다시', '결국', '즉', '그래도'
]
stopwords = list(set(stopwords))

okt = Okt()

def process_description(description: str) -> pd.DataFrame:
    nouns = okt.nouns(description)
    
    filtered_nouns = [noun for noun in nouns if noun not in stopwords]
    
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

def main():
    descriptions = []
    
    print("책 취향을 입력하세요. 종료하려면 '종료'를 입력하세요.")
    
    while True:
        description = input("입력: ")
        if description.lower() == '종료':
            break
        descriptions.append(description)
    
    combined_description = ' '.join(descriptions)
    
    processed_df = process_description(combined_description)
    
    save_to_csv(processed_df, 'processed_description.csv')
    
    print("CSV 파일 저장 완료.")

if __name__ == "__main__":
    main()