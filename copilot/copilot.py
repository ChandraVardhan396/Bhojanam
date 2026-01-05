from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import os

from bridge import CopilotBridge

class CopilotWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setFixedSize(420, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web = QWebEngineView(self)
        # IMPORTANT: remove white background from WebEngine
        self.web.setAttribute(Qt.WA_TranslucentBackground, True)
        self.web.setStyleSheet("background: transparent;")

        page = self.web.page()
        page.setBackgroundColor(QColor(0, 0, 0, 0))


        # WebChannel
        self.channel = QWebChannel()
        self.bridge = CopilotBridge()
        self.channel.registerObject("copilot", self.bridge)
        self.web.page().setWebChannel(self.channel)
        

        base_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(base_dir, "ui", "index.html")

        self.web.load(QUrl.fromLocalFile(html_path))
        layout.addWidget(self.web)
        self.web.page().windowCloseRequested.connect(self.hide)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
