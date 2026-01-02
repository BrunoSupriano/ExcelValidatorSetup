
from PySide6.QtGui import QColor, QFont

class Theme:
    # Colors
    PRIMARY = "#007b5e"
    BACKGROUND = "#1e1e1e"
    SURFACE = "#2d2d2d"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#b0b0b0"
    ERROR = "#cf6679"
    WARNING = "#ffb74d"
    SUCCESS = "#81c784"
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    HEADER_SIZE = 16
    BODY_SIZE = 12

    # Glassmorphism style for main window
    STYLESHEET = """
    QMainWindow {
        background-color: #1e1e1e;
    }
    QWidget {
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #ffffff;
    }
    /* Cards */
    QFrame#GlassCard {
        background-color: rgba(45, 45, 45, 200);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 30);
    }
    /* Buttons */
    QPushButton {
        background-color: #007b5e;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        color: white;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #009670;
    }
    QPushButton:pressed {
        background-color: #006048;
    }
    QPushButton#SecondaryButton {
        background-color: transparent;
        border: 1px solid #007b5e;
        color: #007b5e;
    }
    QPushButton#SecondaryButton:hover {
        background-color: rgba(0, 123, 94, 20);
    }
    
    /* Scrollbars */
    QScrollBar:vertical {
        border: none;
        background: #1e1e1e;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #444;
        min-height: 20px;
        border-radius: 5px;
    }
    """
