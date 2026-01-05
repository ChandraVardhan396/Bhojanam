from PySide6.QtWidgets import QWidget, QMenu, QApplication
from PySide6.QtCore import Qt, QRect # Added QRect
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap # Added QPixmap
from copilot import CopilotWindow
from PySide6.QtGui import QPainter, QColor, QPixmap, QIcon, QPen
from PySide6.QtCore import Qt, QRect
import sys

class FloatingIcon(QWidget):
    def __init__(self):
        super().__init__()
        # 1. Load the icon as a Pixmap for drawing
        self.icon_pixmap = QIcon("Bhojam.ico").pixmap(40, 40) # Size slightly smaller than 56
        
        self.setFixedSize(56, 56)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.drag_pos = None
        self.copilot = CopilotWindow()
        self.copilot.hide()

        self.menu = QMenu(self)
        close_action = self.menu.addAction("Close")
        close_action.triggered.connect(self.exit_app)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Draw the dark background circle
        painter.setBrush(QColor(30, 30, 30, 230)) # Slightly more opaque for better contrast
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 56, 56)

        # 2. Draw the Icon - Made BIGGER (52x52 instead of 40x40)
        # We load a high-quality version of the pixmap
        icon_pixmap = QIcon("Bhojam.ico").pixmap(52, 52)
        if not icon_pixmap.isNull():
            # Centering a 52px icon in a 56px widget: (56-52)/2 = 2px margin
            icon_rect = QRect(2, 2, 52, 52) 
            painter.drawPixmap(icon_rect, icon_pixmap)

        # 3. Draw a THIN purple border on the very edge
        thin_purple_pen = QPen(QColor(160, 100, 255, 200)) # Purple with some transparency
        thin_purple_pen.setWidthF(1.5) # Use setWidthF for sub-pixel thinness
        painter.setPen(thin_purple_pen)
        painter.setBrush(Qt.NoBrush)
        
        # Draw the ring just inside the boundary to avoid clipping
        painter.drawEllipse(1, 1, 54, 54)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.menu.exec(event.globalPosition().toPoint())
        elif event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            if self.copilot.isVisible():
                self.copilot.move(self.copilot.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

    def toggle_copilot(self):
        if self.copilot.isVisible():
            self.copilot.hide()
        else:
            self.copilot.move(self.x() + 70, self.y())
            self.copilot.show()
            self.copilot.raise_()
            self.copilot.activateWindow()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_copilot()

    def exit_app(self):
        self.copilot.close()
        QApplication.quit()