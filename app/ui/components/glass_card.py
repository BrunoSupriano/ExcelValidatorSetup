
from PySide6.QtWidgets import QFrame, QVBoxLayout
from ..theme import Theme

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        # Style is defined in Theme.STYLESHEET under QFrame#GlassCard
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
