
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from ..components.glass_card import GlassCard
from ..theme import Theme

class ValidationView(QWidget):
    back_requested = Signal()
    process_requested = Signal()
    ignore_errors_requested = Signal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        self.card = GlassCard()
        self.layout.addWidget(self.card)

        # Header
        lbl_title = QLabel("Validação Estrutural")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.PRIMARY};")
        self.card.layout.addWidget(lbl_title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Arquivo", "Mensagem", "Severidade"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: rgba(0,0,0,0.2);
                border: none;
                gridline-color: #444;
            }}
            QHeaderView::section {{
                background-color: {Theme.SURFACE};
                padding: 5px;
                border: none;
                color: #aaa;
            }}
        """)
        self.card.layout.addWidget(self.table)

        # Status Label
        self.lbl_status = QLabel("Aguardando validação...")
        self.lbl_status.setStyleSheet("font-size: 14px; margin-top: 10px;")
        self.card.layout.addWidget(self.lbl_status)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_back = QPushButton("← Voltar")
        self.btn_back.setObjectName("SecondaryButton")
        self.btn_back.clicked.connect(self.back_requested.emit)
        
        self.btn_ignore = QPushButton("Ignorar Erros e Prosseguir")
        self.btn_ignore.setStyleSheet(f"background-color: {Theme.WARNING}; color: #222; font-weight: bold;")
        self.btn_ignore.clicked.connect(self.ignore_errors_requested.emit)
        self.btn_ignore.setVisible(False)

        self.btn_process = QPushButton("Processar Dados →")
        self.btn_process.clicked.connect(self.process_requested.emit)
        self.btn_process.setEnabled(False)

        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_ignore)
        btn_layout.addWidget(self.btn_process)
        self.card.layout.addLayout(btn_layout)

    def set_errors(self, errors):
        self.table.setRowCount(0)
        critical_count = 0
        
        for err in errors:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(err.file_name))
            self.table.setItem(row, 1, QTableWidgetItem(err.message))
            
            item_severity = QTableWidgetItem(err.severity.upper())
            color = Theme.ERROR if err.severity == "critical" else Theme.WARNING
            item_severity.setForeground(QColor(color))
            self.table.setItem(row, 2, item_severity)

            if err.severity == "critical":
                critical_count += 1
        
        # Reset visibility
        self.btn_ignore.setVisible(False)

        if critical_count > 0:
            self.lbl_status.setText(f"Encontrados {critical_count} erros críticos. Corrija os arquivos para continuar.")
            self.lbl_status.setStyleSheet(f"color: {Theme.ERROR};")
            self.btn_process.setEnabled(False)
            self.btn_process.setStyleSheet("background-color: #444;")
            
            self.btn_ignore.setVisible(True)
        elif not errors:
            self.lbl_status.setText("Todos os arquivos estão válidos!")
            self.lbl_status.setStyleSheet(f"color: {Theme.SUCCESS};")
            self.btn_process.setEnabled(True)
            self.btn_process.setStyleSheet(f"background-color: {Theme.PRIMARY};")
        else:
            self.lbl_status.setText("Avisos encontrados, mas é possível prosseguir.")
            self.lbl_status.setStyleSheet(f"color: {Theme.WARNING};")
            self.btn_process.setEnabled(True)
            self.btn_process.setStyleSheet(f"background-color: {Theme.PRIMARY};")
