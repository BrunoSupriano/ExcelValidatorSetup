

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt, QPoint, QThread, Signal
from .components.title_bar import TitleBar
from .views.import_view import ImportView
from .views.validation_view import ValidationView
from .views.processing_view import ProcessingView
from .theme import Theme
from ..core.excel_handler import ExcelHandler
from ..core.validator import Validator
from ..core.processor import Processor
import pandas as pd

import traceback

class Worker(QThread):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, str)
    
    def __init__(self, task_func, *args):
        super().__init__()
        self.task_func = task_func
        self.args = args # This is a tuple. 

    def run(self):
        try:
            # Pass signal emitter as first arg
            # NOTE: We must ensure all task_funcs called by Worker are updated to accept this arg!
            result = self.task_func(self.progress.emit, *self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e) + "\n" + traceback.format_exc())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Validator Pro")
        self.resize(1000, 700)
        
        # Frameless Window Setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # REMOVED for stability
        
        # Custom Dragging
        self.drag_pos = QPoint()
        
        # Central Widget
        self.central_widget = QWidget()
        self.central_widget.setObjectName("Container")
        self.central_widget.setStyleSheet(f"""
            QWidget#Container {{
                background-color: {Theme.BACKGROUND};
                border: 1px solid #333;
                border-radius: 10px;
            }}
        """)
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Title Bar
        self.title_bar = TitleBar(self)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        self.layout.addWidget(self.title_bar)
        
        # Content Area
        self.content_area = QStackedWidget()
        self.layout.addWidget(self.content_area)
        
        # Views
        self.import_view = ImportView()
        self.validation_view = ValidationView()
        self.processing_view = ProcessingView()
        
        self.content_area.addWidget(self.import_view)      # Index 0
        self.content_area.addWidget(self.validation_view)  # Index 1
        self.content_area.addWidget(self.processing_view)  # Index 2
        
        # Connections
        self.import_view.next_step_requested.connect(self.start_validation)
        self.validation_view.back_requested.connect(lambda: self.content_area.setCurrentIndex(0))
        self.validation_view.process_requested.connect(self.start_processing)
        self.validation_view.ignore_errors_requested.connect(self.on_ignore_errors)
        self.validation_view.ignore_errors_requested.connect(self.on_ignore_errors)
        self.processing_view.reset_requested.connect(self.reset_app)
        self.processing_view.save_requested.connect(self.start_save)
        
        # State
        self.loaded_dfs = {}
        self.last_errors = []

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def start_drag(self, global_pos):
        self.drag_pos = global_pos - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
             self.move(event.globalPosition().toPoint() - self.drag_pos)
        super().mouseMoveEvent(event)
        
    def start_save(self, df, path):
        """Starts saving in background."""
        from .components.loading_dialog import LoadingDialog
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.set_progress(0, "Preparando gravação...")
        self.loading_dialog.show()
        
        # We reuse the Worker class
        # Worker(task_func, *args)
        # task_func signature: (progress_callback, *args)
        
        self.save_worker = Worker(self._save_task, df, path)
        self.save_worker.finished.connect(self.on_save_finished)
        self.save_worker.error.connect(self.on_error)
        self.save_worker.progress.connect(self.update_loading_progress)
        self.save_worker.start()
        
    def _save_task(self, progress_callback, df, path):
         # Pass callback to handler for real progress
         from ..core.excel_handler import ExcelHandler
         ExcelHandler.save_excel(df, path, progress_callback)
         return path # Return path for opening
         
    def on_save_finished(self, result_path):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        # Show Custom Success Dialog
        from .components.success_dialog import SuccessDialog
        import os
        
        dialog = SuccessDialog(self, result_path)
        if dialog.exec(): # Accepted (Open File)
            try:
                os.startfile(result_path)
            except Exception as e:
                print(f"Error opening file: {e}")

    # Logic Flow
    def start_validation(self, file_paths):
        # Validation View Loading State
        from .components.loading_dialog import LoadingDialog
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        
        self.worker = Worker(self._load_and_validate, file_paths)
        self.worker.finished.connect(self.on_validation_finished)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.update_loading_progress)
        self.worker.start()

    def update_loading_progress(self, percent, message):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.set_progress(percent, message)
        
    def _load_and_validate(self, progress_callback, file_paths):
        # 1. Load (manual loop)
        dfs = {}
        total = len(file_paths)
        from pathlib import Path
        total_size_bytes = 0
        
        for i, path in enumerate(file_paths):
            p = int((i / total) * 50)
            progress_callback(p, "Lendo arquivos...")
            try:
                path_obj = Path(path)
                # Calculate size
                if path_obj.exists():
                     total_size_bytes += path_obj.stat().st_size
                
                print(f"Loading '{path}' (Name: {path_obj.name})") # DEBUG
                df = pd.read_excel(path_obj, engine='openpyxl')
                dfs[str(path)] = df # Use full path as key to avoid collisions
            except Exception as e:
                print(f"Skipping {path}: {e}")
        
        progress_callback(50, "Validando...")
        
        # 2. Validate Structure
        all_errors = []
        count = 0
        for name, df in dfs.items():
            errs = Validator.validate_structure(name, df)
            all_errors.extend(errs)
            
            count += 1
            p = 50 + int((count / len(dfs)) * 40)
            progress_callback(p, "Validando...")
            
        progress_callback(90, "Comparando colunas...")
        
        # 3. Compare
        match, compare_errors = Validator.compare_columns(dfs)
        all_errors.extend(compare_errors)
        
        progress_callback(100, "Concluído!")
        
        return dfs, all_errors, total_size_bytes

    def on_validation_finished(self, result):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        self.loaded_dfs, errors, total_size = result
        self.last_errors = errors # Store for ignore processing
        self.total_input_size_mb = total_size / (1024 * 1024)
        
        # Setup Validation View
        if not errors:
            self.start_processing()
        else:
            self.validation_view.set_errors(errors)
            self.content_area.setCurrentIndex(1)
        
    def on_ignore_errors(self):
        """Removes files with critical errors and proceeds with the rest."""
        if not self.last_errors:
            self.start_processing()
            return
            
        # Identify files to remove
        files_to_remove = set()
        for err in self.last_errors:
            if err.severity == "critical" and err.full_path:
                files_to_remove.add(err.full_path)
        
        # Remove from loaded_dfs
        if files_to_remove:
            print(f"Removing invalid files: {files_to_remove}")
            for path in files_to_remove:
                if path in self.loaded_dfs:
                    del self.loaded_dfs[path]
        
        # Check if anything remains
        if not self.loaded_dfs:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Sem arquivos", "Todos os arquivos selecionados contêm erros críticos e foram removidos.")
            self.content_area.setCurrentIndex(0) # Go back to import
            return
            
        # Proceed with valid files
        self.start_processing()
        
    def start_processing(self):
        # Loading State (Overlay)
        from .components.loading_dialog import LoadingDialog
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()
        
        self.proc_worker = Worker(self._process_data, self.loaded_dfs)
        self.proc_worker.finished.connect(self.on_processing_finished)
        self.proc_worker.error.connect(self.on_error)
        self.proc_worker.progress.connect(self.update_loading_progress)
        self.proc_worker.start()
        
    def _process_data(self, progress_callback, dfs):
        # Calculate stats BEFORE processing
        total_input_rows = sum(len(df) for df in dfs.values())
        
        # Collect initial columns
        if dfs:
            first_df = next(iter(dfs.values()))
            input_cols_list = set(first_df.columns)
            input_cols_count = len(input_cols_list)
        else:
            input_cols_list = set()
            input_cols_count = 0
        
        # 1. Concat
        progress_callback(10, "Unificando dados...")
        
        # Filter empty/NA frames to avoid FutureWarning
        valid_dfs = [df for df in dfs.values() if not df.empty and not df.isna().all().all()]
        
        if valid_dfs:
            combined = pd.concat(valid_dfs, ignore_index=True)
        else:
            combined = pd.DataFrame()
        
        # 2. Process
        progress_callback(30, "Aplica regras de negócio...")
        processed = Processor.process_dataframe(combined)
        
        progress_callback(100, "Finalizando...")
        
        # Final Stats
        output_cols_list = set(processed.columns)
        new_cols = list(output_cols_list - input_cols_list)
        
        # Estimate output MB (Using deep memory usage as proxy for raw data size)
        # XLSX is zip-compressed XML. Pandas memory usage is uncompressed Python objects.
        # Heuristic: Real XLSX is ~1/8th of Pandas Deep Memory for text-heavy data.
        mem_usage = processed.memory_usage(deep=True).sum()
        est_output_mb = (mem_usage / (1024 * 1024)) / 7.5 
        
        stats = {
            'input_rows': total_input_rows,
            'output_rows': len(processed),
            'input_cols': input_cols_count,
            'output_cols': len(processed.columns),
            'new_cols': new_cols,
            'input_mb': getattr(self, 'total_input_size_mb', 0),
            'output_mb': est_output_mb
        }
        
        return processed, stats

    def on_processing_finished(self, result):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        df, stats = result
        self.processing_view.on_success(df, stats)
        self.content_area.setCurrentIndex(2)
        
    def on_error(self, msg):
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.close()
            
        # Simple error handling
        print(f"Erro: {msg}")
        if self.content_area.currentIndex() == 2:
            self.processing_view.on_error(msg)

    def reset_app(self):
        self.import_view.clear_files()
        self.loaded_dfs = {}
        self.content_area.setCurrentIndex(0)

