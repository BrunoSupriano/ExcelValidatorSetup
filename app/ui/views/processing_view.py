
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QFileDialog, QFrame, QGridLayout, QSizePolicy
from PySide6.QtCore import Signal, Qt
from ..components.glass_card import GlassCard
from ..components.success_animation import SuccessAnimation
from ..theme import Theme

class StatRow(QWidget):
    def __init__(self, label, value, color=None, subtext=None):
        super().__init__()
        self.setFixedHeight(50) # Fixed height for alignment across cards
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)
        
        # Value
        lbl_val = QLabel(str(value))
        c = color if color else "white"
        lbl_val.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c};")
        layout.addWidget(lbl_val)
        
        # Label
        lbl_name = QLabel(label)
        lbl_name.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(lbl_name)

class GroupCard(QFrame):
    def __init__(self, title, items, is_after=False):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 5);
                border-radius: 10px;
                border: none;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        t_color = Theme.PRIMARY if is_after else "#888"
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(f"color: {t_color}; font-weight: bold; letter-spacing: 1px; font-size: 12px; margin-bottom: 5px;")
        layout.addWidget(lbl_title)
        
        # Items
        for item in items:
            # item = (Label, Value, Color)
            label, val, col = item
            row = StatRow(label, val, col)
            layout.addWidget(row)
            
            # Divider (except last?) keep simple for now
            
        layout.addStretch()

class ProcessingView(QWidget):
    reset_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.card = GlassCard()
        self.layout.addWidget(self.card)
        
        # -- SUCCESS STATE UI --
        self.success_container = QWidget()
        vbox_success = QVBoxLayout(self.success_container)
        vbox_success.setAlignment(Qt.AlignCenter)
        
        self.animation = SuccessAnimation()
        vbox_success.addWidget(self.animation, alignment=Qt.AlignCenter)
        
        lbl_success = QLabel("Processamento Concluído!")
        lbl_success.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {Theme.SUCCESS}; margin-top: 10px; margin-bottom: 20px;")
        lbl_success.setAlignment(Qt.AlignCenter)
        vbox_success.addWidget(lbl_success)
        
        # Split Container
        self.split_layout = QHBoxLayout()
        self.split_layout.setSpacing(20)
        self.split_layout.setContentsMargins(20, 0, 20, 0)
        vbox_success.addLayout(self.split_layout)
        
        # Extras (New Cols etc)
        self.extras_layout = QVBoxLayout()
        vbox_success.addLayout(self.extras_layout)
        
        # Close Animation UI initially
        self.success_container.setVisible(False)
        self.card.layout.addWidget(self.success_container)

        # -- LOADING/PROCESSING STATE UI --
        self.loading_container = QWidget()
        vbox_loading = QVBoxLayout(self.loading_container)
        
        lbl_title = QLabel("Processamento")
        lbl_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.PRIMARY};")
        vbox_loading.addWidget(lbl_title)
        
        self.lbl_info = QLabel("Inicializando...")
        vbox_loading.addWidget(self.lbl_info)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"""
            QProgressBar {{ border: 2px solid #444; border-radius: 5px; text-align: center; background-color: #222; }}
            QProgressBar::chunk {{ background-color: {Theme.PRIMARY}; }}
        """)
        vbox_loading.addWidget(self.progress)
        
        self.card.layout.addWidget(self.loading_container)
        
        # -- ACTIONS --
        self.btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Salvar Relatório FInal")
        self.btn_save.setStyleSheet(f"background-color: {Theme.SUCCESS}; font-size: 14px; padding: 12px;")
        self.btn_save.clicked.connect(self.save_file)
        
        self.btn_new = QPushButton("Novo Processamento")
        self.btn_new.setObjectName("SecondaryButton")
        self.btn_new.clicked.connect(self.reset_requested.emit)
        
        self.btn_layout.addWidget(self.btn_new)
        self.btn_layout.addWidget(self.btn_save)
        
        self.btn_layout_widget = QWidget()
        self.btn_layout_widget.setLayout(self.btn_layout)
        self.btn_layout_widget.setVisible(False) 
        self.card.layout.addWidget(self.btn_layout_widget)
        
        self.final_df = None

    def set_progress(self, value, message=None):
        self.progress.setValue(value)
        if message:
            self.lbl_info.setText(message)

    def on_success(self, df, stats):
        self.final_df = df
        
        # Switch UI
        self.loading_container.setVisible(False)
        self.success_container.setVisible(True)
        self.btn_layout_widget.setVisible(True)
        
        # Start Animation
        self.animation.start()
        
        # --- DATA PREP ---
        input_mb = stats.get('input_mb', 0)
        output_mb = stats.get('output_mb', 0)
        input_rows = stats.get('input_rows', 0)
        output_rows = stats.get('output_rows', 0)
        input_cols = stats.get('input_cols', 0)
        output_cols = stats.get('output_cols', 0)
        
        # --- LOGIC FOR COLORS ---
        # Size: Lower = Green, Higher = Red
        if output_mb < input_mb:
            c_size = Theme.SUCCESS # Green
        elif output_mb > input_mb:
            c_size = Theme.ERROR   # Red
        else:
            c_size = "white"
            
        # Rows: Equal = Green, Lower = Red
        if output_rows == input_rows:
            c_rows = Theme.SUCCESS
        elif output_rows < input_rows:
            c_rows = Theme.ERROR
        else:
            c_rows = "white" # Higher rows?
            
        # Cols: Higher = Green
        if output_cols > input_cols:
            c_cols = Theme.SUCCESS
        elif output_cols < input_cols:
            c_cols = Theme.ERROR # Lost columns?
        else:
            c_cols = "white"

        # --- BUILD CARDS ---
        # Clear layout
        while self.split_layout.count():
            item = self.split_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # BEFORE CARD (Gray theme)
        before_items = [
            ("Tamanho Total", f"{input_mb:.2f} MB", "#aaa"),
            ("Linhas", f"{input_rows:,}", "#aaa"),
            ("Colunas", f"{input_cols}", "#aaa")
        ]
        card_before = GroupCard("ANTES", before_items, is_after=False)
        self.split_layout.addWidget(card_before)
        
        # ARROW (Optional, simple label)
        lbl_arrow = QLabel("→")
        lbl_arrow.setStyleSheet("font-size: 20px; color: #444; font-weight: bold;")
        lbl_arrow.setAlignment(Qt.AlignCenter)
        self.split_layout.addWidget(lbl_arrow)
        
        # AFTER CARD (Colored theme)
        after_items = [
            ("Tamanho Final", f"{output_mb:.2f} MB", c_size),
            ("Linhas", f"{output_rows:,}", c_rows),
            ("Colunas", f"{output_cols}", c_cols)
        ]
        card_after = GroupCard("DEPOIS", after_items, is_after=True)
        self.split_layout.addWidget(card_after)
        
        # --- EXTRAS ---
        while self.extras_layout.count():
            item = self.extras_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        new_cols = stats.get('new_cols', [])
        if new_cols:
            lbl_new = QLabel(f"Colunas Adicionadas: {', '.join(new_cols)}")
            lbl_new.setWordWrap(True)
            lbl_new.setStyleSheet("color: #007b5e; font-style: italic; font-size: 11px; margin-top: 15px;")
            lbl_new.setAlignment(Qt.AlignCenter)
            self.extras_layout.addWidget(lbl_new)
        
    def on_error(self, message):
        self.lbl_info.setText("Erro!")
        self.lbl_info.setStyleSheet(f"color: {Theme.ERROR};")
        self.btn_layout_widget.setVisible(True)
        self.btn_save.setVisible(False)

    def save_file(self):
        if self.final_df is None: return
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%d%m%Y.%H%M%S")
        default_name = f"Relatorio_Clean_{timestamp}.xlsx"
        
        path, _ = QFileDialog.getSaveFileName(self, "Salvar", default_name, "Excel Files (*.xlsx)")
        if path:
            try:
                from ...core.excel_handler import ExcelHandler
                ExcelHandler.save_excel(self.final_df, path)
            except Exception as e:
                pass
