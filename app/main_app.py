
import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.ui.theme import Theme

def main():
    app = QApplication(sys.argv)
    
    # Apply global theme
    app.setStyleSheet(Theme.STYLESHEET)
    
    # Show Rich UI
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
