
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSizeGrip
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QPalette
from .title_bar import TitleBar
from .styles import Styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Processor")
        self.resize(800, 600)
        
        # Helper to track dragging
        self.dragging = False
        self.drag_position = QPoint()

        # Frameless Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint)
        # REMOVED: self.setAttribute(Qt.WA_TranslucentBackground) to fix rendering artifacts
        # self.setAttribute(Qt.WA_TranslucentBackground) 
        self.setStyleSheet(Styles.MAIN_WINDOW)

        # Central Widget & Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Title Bar
        self.title_bar = TitleBar("Excel Processor", self)
        self.title_bar.minimized.connect(self.showMinimized)
        self.title_bar.maximized.connect(self.toggle_maximize)
        self.title_bar.closed.connect(self.close)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Content Area (To be filled by implementation)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.addWidget(self.content_area)
        
        # Size Grip for resizing (bottom-right)
        self.size_grip = QSizeGrip(self.central_widget)
        self.size_grip.setStyleSheet("background: transparent; width: 20px; height: 20px;")
        
        # We need to manually handle layout of size grip if using absolute positioning or just let it float
        # But QSizeGrip in a layout usually sits in a corner. 
        # For a clean overlay, we might re-parent it or add it to bottom of layout.
        # Simplified: Stick it in the layout for now or overlay it in resizeEvent.

    def resizeEvent(self, event):
        rect = self.rect()
        self.size_grip.move(rect.right() - self.size_grip.width(), rect.bottom() - self.size_grip.height())
        super().resizeEvent(event)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # --- Drag Logic ---
    def mousePressEvent(self, event):
        # Allow dragging only from title bar area (approximate check usually done strictly on title bar widget)
        # But since we have a custom title bar widget, we should let it handle the click start.
        # Alternatively, rely on the TitleBar's mouse events bubbling up if ignored, 
        # OR check if click is within title bar geometry.
        
        # Better approach: The TitleBar receives the press. We can install an event filter or just handle it here 
        # if the user clicks on the background.
        
        if event.button() == Qt.LeftButton:
            # Check if click is in title bar area (local coordinates)
            if self.childAt(event.position().toPoint()) is self.title_bar or \
               self.title_bar.geometry().contains(event.position().toPoint()):
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
