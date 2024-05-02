import pandas as pd

# this is the list that not need for analytics
BLACKLIST = ['library', 'audio', 'books', 'audiobook', 'read', 'tobuy', 'ebook', 'ya', 'ownedbooks', 'default',
             'readin', 'kindle', 'bookclub', 'series', 'booksiown', 'owned', 'currentlyreading', 'favourites',
             'favorites', 'ebooks', 'childrens', 'toread', 'audiobooks']


class BookData:
    def __init__(self, series: pd.Series):
        self.SERIES = series
        self.NAME = series["original_title"].get(0)
        self.AVERAGE_RATING = series["average_rating"].get(0)
        self.RAW_TAGS = [val.strip() for sublist in series["tag_name"].copy().dropna().str.split(",").tolist() for val
                         in sublist]
        self.__filtered_tags = None

    def get_filtered_tags(self):
        if self.__filtered_tags is None:
            self.__filtered_tags = list(filter(lambda tag: tag not in BLACKLIST, self.RAW_TAGS))

        return self.__filtered_tags


class RawDataProcessor:

    def __init__(self, path: str):
        self.__NAMES_INDEX = None
        self.PATH = path
        self.DATA = pd.read_csv(self.PATH)
        self.DATA.reset_index(drop=True, inplace=True)

    def getBookNames(self) -> pd.Series:
        if self.__NAMES_INDEX is None:
            self.__NAMES_INDEX = self.DATA["original_title"].copy()

        return self.__NAMES_INDEX.copy()

    def getBookInfo(self, name: str) -> pd.Series:
        return self.DATA[self.DATA["original_title"] == name]

    def getBookData(self, name: str) -> BookData:
        return BookData(self.getBookInfo(name))


processor = RawDataProcessor("../datasets/books_updated.csv")
# print(processor.getBookNames())
print(processor.getBookInfo("The Hunger Games"))
data = BookData(processor.getBookInfo("The Hunger Games"))
print(data)
