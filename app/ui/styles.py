class Styles:
    DARK_BACKGROUND = "#1E1E1E"
    GLASS_BACKGROUND = "#2b2b2b" # Solid Dark Grey
    TEXT_COLOR = "#FFFFFF"
    ACCENT_COLOR = "#6C5CE7"
    BORDER_COLOR = "#333333"
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {GLASS_BACKGROUND}; 
        }}
        QWidget#centralWidget {{
            background-color: {GLASS_BACKGROUND};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px; /* Reduced radius for solid window */
        }}
    """
    
    # ⭐ CORREÇÃO AQUI - Remover estilos de QPushButton
    TITLE_BAR = f"""
        TitleBar {{
            background-color: transparent;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        }}
        TitleBar QLabel {{
            color: {TEXT_COLOR};
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: bold;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {ACCENT_COLOR};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-family: 'Segoe UI';
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #5A4ECC;
        }}
        QPushButton:pressed {{
            background-color: #483DAD;
        }}
    """
    
    LABEL_STATUS = f"""
        QLabel {{
            color: rgba(255, 255, 255, 180);
            font-size: 12px;
            font-family: 'Segoe UI';
        }}
    """