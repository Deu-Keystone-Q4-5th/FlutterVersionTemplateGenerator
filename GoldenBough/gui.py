import asyncio
import os
import sys
import urllib.request

import aiohttp
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QGridLayout,
                             QPushButton, QLineEdit, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication


class BookInfoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("책 정보 검색")

        # CSV 파일 로딩
        self.books_df = pd.read_csv("books.csv", dtype={'cover': str})

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
        self.book_table.setColumnCount(19)
        self.book_table.setHorizontalHeaderLabels([
            "표지", "제목", "링크", "저자", "출판일", "설명", "ISBN", "ISBN13", "아이템ID",
            "판매가", "정가", "몰 타입", "재고 상태", "마일리지", "카테고리 ID",
            "카테고리 이름", "출판사", "판매 포인트", "성인 여부"
        ])
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 테이블 수정 방지
        grid_layout.addWidget(self.book_table, 1, 0, 1, 3)

        # 처음에 모든 책 정보를 표시
        self.current_page = 1
        asyncio.run(self.update_table(self.books_df))


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
        self.update_table(filtered_books)

    async def update_table(self, data: pd.DataFrame):
        print("update")
        self.book_table.setRowCount(len(data))

        for row, book in enumerate(data.itertuples()):
            # 나머지 정보 설정
            for col, value in enumerate(book[1:]):  # 첫 번째 열은 인덱스이므로 제외
                if isinstance(value, str):
                    item = QTableWidgetItem(value)
                else:
                    item = QTableWidgetItem(str(value))  # 숫자형 데이터를 문자열로 변환
                self.book_table.setItem(row, col + 1, item)

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
                        pixmap = pixmap.scaledToWidth(100)
                        cover_label.setPixmap(pixmap)
                    else:
                        print(f"Image loading error: {response.status}")

        tasks = [load_cover(row, book) for row, book in enumerate(data.itertuples())]
        await asyncio.gather(*tasks)

        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < 2)
    def show_prev_page(self):

        if self.current_page > 1:
            self.current_page -= 1
            # TODO : set csv
            self.update_table(self.books_df)

    def show_next_page(self):
        print('run next')

        self.current_page += 1
        asyncio.run(self.update_table(self.books_df))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.book_table.resizeColumnsToContents()  # 컬럼 너비 자동 조정


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = BookInfoGUI()
    window.show()
    sys.exit(app.exec_())