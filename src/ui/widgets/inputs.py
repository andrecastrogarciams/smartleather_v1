from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt

class IndustrialInput(QLineEdit):
    """
    Campo de entrada estilo industrial sem bordas superiores, 
    com destaque inferior dinâmico.
    """
    def __init__(self, placeholder="", is_password=False, parent=None):
        super().__init__(parent)
        self.setObjectName("IndustrialInput")
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(60)
        
        if is_password:
            self.setEchoMode(QLineEdit.Password)
