
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem, QAbstractItemView
from PySide6.QtCore import Qt, Signal, QMimeData, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from ..components.glass_card import GlassCard
from ..theme import Theme

class DropArea(QLabel):
    files_dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setText("Arraste seus arquivos Excel aqui\nou clique para selecionar")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #444;
                border-radius: 10px;
                color: #888;
                font-size: 16px;
                background-color: rgba(0,0,0,0.2);
            }
            QLabel:hover {
                border-color: #007b5e;
                color: #007b5e;
                background-color: rgba(0, 123, 94, 0.1);
            }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile().endswith('.xlsx')]
        if files:
            self.files_dropped.emit(files)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos", "", "Excel Files (*.xlsx)")
            if files:
                self.files_dropped.emit(files)

class ImportView(QWidget):
    next_step_requested = Signal(list) # Emits list of file paths

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.file_paths = []

        # Card
        self.card = GlassCard()
        self.layout.addWidget(self.card)

        # Header
        lbl_title = QLabel("Importação de Arquivos")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.PRIMARY};")
        self.card.layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Selecione todos os arquivos que deseja unificar e processar.")
        lbl_desc.setStyleSheet("color: #aaa; margin-bottom: 20px;")
        self.card.layout.addWidget(lbl_desc)

        # Drop Area
        self.drop_area = DropArea()
        self.drop_area.setFixedHeight(120)
        self.drop_area.files_dropped.connect(self.add_files)
        self.card.layout.addWidget(self.drop_area)
        
        # Counter Label
        self.lbl_counter = QLabel("Nenhum arquivo selecionado")
        self.lbl_counter.setStyleSheet("color: #888; margin-top: 10px; font-style: italic;")
        self.card.layout.addWidget(self.lbl_counter)

        # List of files (Grid Mode)
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.IconMode)
        self.file_list.setIconSize(QSize(48, 48))
        self.file_list.setResizeMode(QListWidget.Adjust)
        self.file_list.setSpacing(10)
        self.file_list.setSelectionMode(QAbstractItemView.NoSelection) # Disable selection for cleaner look
        self.file_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent; 
                border: 1px solid #444; 
                border-radius: 5px;
                padding: 10px;
            }}
            QListWidget::item {{
                color: white;
                background: transparent;
            }}
            QListWidget::item:hover {{
                background: rgba(255, 255, 255, 10);
                border-radius: 5px;
            }}
        """)
        self.card.layout.addWidget(self.file_list)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Limpar Lista")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_files)
        
        self.btn_next = QPushButton("Validar Arquivos →")
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.on_next)

        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_next)
        self.card.layout.addLayout(btn_layout)
        
        # Prepare File Icon
        self.file_icon = self._generate_file_icon()

    def _generate_file_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw Document Shape
        painter.setBrush(QColor("#107c41")) # Excel Green
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(10, 5, 44, 54, 4, 4)
        
        # Draw 'X' or lines
        painter.setPen(QColor("white"))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "XLSX")
        
        painter.end()
        return QIcon(pixmap)

    def add_files(self, paths):
        for path in paths:
            if path not in self.file_paths:
                self.file_paths.append(path)
                
                # Add Grid Item
                filename = path.split('/')[-1]
                item = QListWidgetItem(self.file_icon, filename)
                item.setToolTip(path)
                self.file_list.addItem(item)
        
        self.update_ui()

    def clear_files(self):
        self.file_paths = []
        self.file_list.clear()
        self.update_ui()

    def update_ui(self):
        count = len(self.file_paths)
        has_files = count > 0
        
        self.btn_next.setEnabled(has_files)
        self.btn_next.setStyleSheet(f"background-color: {Theme.PRIMARY if has_files else '#444'};")
        
        if count == 0:
            self.lbl_counter.setText("Nenhum arquivo selecionado")
        else:
            s_str = "s" if count > 1 else ""
            self.lbl_counter.setText(f"{count} arquivo{s_str} selecionado{s_str}")

    def on_next(self):
        self.next_step_requested.emit(self.file_paths)
