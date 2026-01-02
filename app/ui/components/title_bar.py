
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from ..theme import Theme

class TitleBar(QWidget):
    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        # Applying the FIXED Solid Dark style
        self.setStyleSheet("""
            QWidget { background: transparent; }
            QLabel { color: white; font-family: 'Segoe UI'; font-size: 14px; font-weight: 500; padding-left: 10px; }
            QPushButton { background: transparent; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); }
            QPushButton#close_btn:hover { background-color: #E81123; }
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 5, 0)
        self.layout.setSpacing(0)
        
        # Title
        self.title_label = QLabel("Excel Validator Pro")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.title_label)
        
        # Fixed Buttons
        self.minimize_btn = self._create_btn('min')
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        
        self.maximize_btn = self._create_btn('max')
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        
        self.close_btn = self._create_btn('close')
        self.close_btn.setObjectName("close_btn")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)

    def _create_btn(self, icon_type):
        btn = QPushButton()
        btn.setFixedSize(46, 30)
        icon = self._generate_icon(icon_type)
        btn.setIcon(icon)
        btn.setIconSize(QSize(12, 12)) 
        return btn

    def _generate_icon(self, icon_type):
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, False)
        
        pen = QPen(Qt.white)
        pen.setWidth(2) 
        painter.setPen(pen)
        
        if icon_type == 'min':
            painter.drawLine(8, 16, 24, 16)
        elif icon_type == 'max':
            painter.drawRect(8, 8, 16, 16)
        elif icon_type == 'close':
            painter.drawLine(8, 8, 24, 24)
            painter.drawLine(24, 8, 8, 24)
            
        painter.end()
        return QIcon(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Delegate drag to parent window if method exists
            window = self.window()
            if hasattr(window, 'start_drag'):
                window.start_drag(event.globalPosition().toPoint())
        super().mousePressEvent(event)
