
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Qt
from ..theme import Theme
from ..components.success_animation import SuccessAnimation

class SuccessDialog(QDialog):
    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container (Glass Card Effect)
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SURFACE};
                border: 1px solid #444;
                border-radius: 15px;
            }}
        """)
        layout.addWidget(container)
        
        self.inner_layout = QVBoxLayout(container)
        self.inner_layout.setContentsMargins(30, 30, 30, 30)
        self.inner_layout.setSpacing(20)
        
        # Animation
        self.anim = SuccessAnimation()
        self.anim.setFixedSize(80, 80)
        self.inner_layout.addWidget(self.anim, alignment=Qt.AlignCenter)
        self.anim.start()
        
        # Title
        lbl_title = QLabel("Sucesso!")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.SUCCESS};")
        lbl_title.setAlignment(Qt.AlignCenter)
        self.inner_layout.addWidget(lbl_title)
        
        # Message
        lbl_msg = QLabel("Arquivo salvo com sucesso.\nDeseja abri-lo agora?")
        lbl_msg.setAlignment(Qt.AlignCenter)
        lbl_msg.setStyleSheet("color: #ddd; font-size: 14px;")
        self.inner_layout.addWidget(lbl_msg)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_close = QPushButton("Fechar")
        self.btn_close.setObjectName("SecondaryButton")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)
        
        self.btn_open = QPushButton("Abrir Arquivo")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SUCCESS};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00b386;
            }}
        """)
        self.btn_open.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_open)
        
        self.inner_layout.addLayout(btn_layout)

    def sizeHint(self):
        return super().sizeHint().expandedTo(self.minimumSizeHint())
