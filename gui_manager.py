import sys
from PyQt5.QtWidgets import QApplication, QWidget
from abc import *
from overrides import final


class WindowGUI(metaclass=ABCMeta):
    """
    윈도우 Abstract Class 입니다. 이걸로 구현해주세요.
    """

    @final
    def __init__(self):
        super.__init__()
        self.initUI()

    @abstractmethod
    def initUI(self):
        pass

    @abstractmethod
    def show(self):
        pass
