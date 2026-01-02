
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from .styles import Styles

class TitleBar(QWidget):
    minimized = Signal()
    maximized = Signal()
    closed = Signal()

    def __init__(self, title="Application", parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        # Apply style for buttons via QSS
        self.setStyleSheet("""
            QWidget { background: transparent; }
            QLabel { color: white; font-family: 'Segoe UI'; font-size: 14px; font-weight: 500; padding-left: 10px; }
            QPushButton { background: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); }
            QPushButton#close_btn:hover { background-color: #E81123; }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 5, 0) # Adjusted margins
        layout.setSpacing(0)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.title_label)
        
        # Buttons with Custom Icons
        self.minimize_btn = self._create_btn('min')
        self.minimize_btn.clicked.connect(self.minimized.emit)
        
        self.maximize_btn = self._create_btn('max')
        self.maximize_btn.clicked.connect(self.maximized.emit)
        
        self.close_btn = self._create_btn('close')
        self.close_btn.setObjectName("close_btn")
        self.close_btn.clicked.connect(self.closed.emit)
        
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)

    def _create_btn(self, icon_type):
        btn = QPushButton()
        btn.setFixedSize(46, 30)
        
        icon = self._generate_icon(icon_type)
        btn.setIcon(icon)
        btn.setIconSize(QSize(12, 12)) 
        
        return btn

    def _generate_icon(self, icon_type):
        """Generates a QIcon in memory drawing white lines on transparent bg."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, False) # Crisp lines
        
        pen = QPen(Qt.white)
        pen.setWidth(2) 
        painter.setPen(pen)
        
        # Drawing coordinates for 32x32 canvas
        # Center is 16,16
        
        if icon_type == 'min':
            # Horizontal line
            painter.drawLine(8, 16, 24, 16)
            
        elif icon_type == 'max':
            # Box
            painter.drawRect(8, 8, 16, 16)
            
        elif icon_type == 'close':
            # X
            painter.drawLine(8, 8, 24, 24)
            painter.drawLine(24, 8, 8, 24)
            
        painter.end()
        return QIcon(pixmap)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)