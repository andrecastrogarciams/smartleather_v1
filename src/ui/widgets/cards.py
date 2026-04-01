from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

class ProductionCard(QWidget):
    """
    Card com fundo branco e sombra suave ambiente ('Layering Principle').
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProductionCard")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(self.layout)
        self._apply_shadow()

    def _apply_shadow(self):
        """Aplica a 'Ambient Shadow' definida no Design System."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        # Cor shadow: rgba(17, 29, 35, 0.06) -> #111d23 com 6% alpha (approx 15 em 255)
        shadow.setColor(QColor(17, 29, 35, 15)) 
        self.setGraphicsEffect(shadow)
        
    def add_widget(self, widget):
        self.layout.addWidget(widget)
