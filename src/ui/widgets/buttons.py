from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class PrimaryButton(QPushButton):
    """
    Botão primário com estilo industrial e áreas de toque grandes (mínimo 48x48px).
    """
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setMinimumHeight(56) # Garantir touch target amigável para RPI
        self.setCursor(Qt.PointingHandCursor)
