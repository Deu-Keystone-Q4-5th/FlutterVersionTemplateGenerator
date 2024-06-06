import asyncio
import sys
import urllib.request
import webbrowser

import aiohttp
import pandas as pd
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QGridLayout,
                             QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem)
from PyQt5.QtWidgets import QWidget, QLabel, QApplication

from GoldenBough.utils import aladin_api_helper, datetimeutils


class BookInfoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("책 정보 검색")
        self.resize(1440, 792)

        # CSV 파일 로딩
        self.books_df = None

        # 레이아웃 설정
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        # 검색 입력 필드
        self.search_input = QLineEdit()
        search_input_label = QLabel("책 제목 또는 ISBN 검색:")
        grid_layout.addWidget(search_input_label, 0, 0)
        grid_layout.addWidget(self.search_input, 0, 1)

        # 페이지 넘기기 버튼
        self.prev_button = QPushButton("이전")
        self.prev_button.clicked.connect(self.show_prev_page)
        self.prev_button.setEnabled(False)  # 처음에는 이전 버튼 비활성화
        grid_layout.addWidget(self.prev_button, 0, 3)

        self.next_button = QPushButton("다음")
        self.next_button.clicked.connect(self.show_next_page)
        grid_layout.addWidget(self.next_button, 0, 4)

        # 검색 버튼
        search_button = QPushButton("검색")
        search_button.clicked.connect(self.search_books)
        grid_layout.addWidget(search_button, 0, 2)

        # 책 정보 표시 테이블
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(18)  # 링크 컬럼 제거
        self.book_table.setHorizontalHeaderLabels([
            "표지", "제목", "저자", "출판일", "설명", "ISBN", "ISBN13", "아이템ID",
            "판매가", "정가", "몰 타입", "재고 상태", "마일리지", "카테고리 ID",
            "카테고리 이름", "출판사", "판매 포인트", "성인 여부"
        ])
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 테이블 수정 방지
        self.book_table.verticalHeader().setDefaultSectionSize(296)  # 행 높이 설정
        grid_layout.addWidget(self.book_table, 1, 0, 1, 5)

        # 처음에 모든 책 정보를 표시
        self.current_page = 1
        asyncio.run(self.update_table())

        # 제목 컬럼 클릭 이벤트 처리
        self.book_table.cellClicked.connect(self.open_link)

    def search_books(self):
        search_term = self.search_input.text()

        # 제목 또는 ISBN으로 검색
        filtered_books = self.books_df[
            (self.books_df['title'].str.contains(search_term, case=False)) |
            (self.books_df['isbn'].str.contains(search_term)) |
            (self.books_df['isbn13'].str.contains(search_term))
        ]

        # 테이블 업데이트
        self.current_page = 1
        asyncio.run(self.update_table(filtered_books))

    async def update_table(self, df: pd.DataFrame = None):
        if df is None:
            await self.set_csv(page=self.current_page)
            df = self.books_df
        self.book_table.setRowCount(len(df))

        for row, book in enumerate(df.itertuples()):
            # 나머지 정보 설정
            for col, value in enumerate(book[1:]):  # 첫 번째 열은 인덱스이므로 제외
                if value == book[13]:  # item image path
                    continue
                if value == book[2]:
                    continue
                if isinstance(value, str):
                    item = QTableWidgetItem(value)
                else:
                    item = QTableWidgetItem(str(value))  # 숫자형 데이터를 문자열로 변환
                modified = col + 1 if col < 2 else col if col < 13 else col - 1
                self.book_table.setItem(row, modified, item)  # 링크 컬럼 제거

        async def load_cover(row, book):
            cover_url = book.cover
            cover_label = QLabel()
            self.book_table.setCellWidget(row, 0, cover_label)

            async with aiohttp.ClientSession() as session:
                async with session.get(cover_url) as response:
                    if response.status == 200:
                        img = await response.read()
                        pixmap = QPixmap()
                        pixmap.loadFromData(img)
                        pixmap = pixmap.scaled(200, 296, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        cover_label.setPixmap(pixmap)
                    else:
                        print(f"Image loading error: {response.status}")

        tasks = [load_cover(row, book) for row, book in enumerate(df.itertuples())]
        await asyncio.gather(*tasks)

        self.prev_button.setEnabled(self.current_page > 1)

    def show_prev_page(self):

        if self.current_page > 1:
            self.current_page -= 1
            asyncio.run(self.update_table())

    def show_next_page(self):

        self.current_page += 1
        asyncio.run(self.update_table())

    async def set_csv(self, year: int = None, month: int = None, week: int = None, page: int = None):
        if year is None:
            year, month, week = datetimeutils.get_month_week()
        if page is None:
            page = 1
        if aladin_api_helper.cache_manager.is_week_cached(year, month, week, page):
            self.books_df = await aladin_api_helper.cache_manager.load_weekly_data(year, month, week, page)
        else:
            self.books_df = await aladin_api_helper.AladinItemListFinder().specific_date(year, month, week).start_page(page).request()

    def open_link(self, row, col):
        if col == 1:  # 제목 컬럼 클릭
            link = self.books_df.iloc[row]['link']
            webbrowser.open_new_tab(link)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.book_table.resizeColumnsToContents()  # 컬럼 너비 자동 조정


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookInfoGUI()
    window.show()
    sys.exit(app.exec_())