
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        painter.translate(w / 2, h / 2)
        painter.rotate(self.angle)
        
        pen = QPen(QColor("#007b5e"))
        pen.setWidth(4)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw arc
        painter.drawArc(-20, -20, 40, 40, 0 * 16, 270 * 16)

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container
        container = QWidget()
        container.setObjectName("LoadingContainer")
        container.setStyleSheet("""
            QWidget#LoadingContainer {
                background-color: #1e1e1e;
                border: none;
                border-radius: 10px;
            }
            QLabel {
                background: transparent;
            }
        """)
        container.setFixedSize(200, 150)
        
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignCenter)
        
        # Spinner
        self.spinner = LoadingSpinner()
        vbox.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Text
        self.label = QLabel("Carregando... 0%")
        self.label.setStyleSheet("color: white; margin-top: 15px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.label, alignment=Qt.AlignCenter)
        
        layout.addWidget(container)

    def set_progress(self, percent, message=None):
        if message:
            self.label.setText(f"{message} {percent}%")
        else:
            self.label.setText(f"Carregando... {percent}%")
