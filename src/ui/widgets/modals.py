from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QFrame, QScrollArea, QWidget, QGridLayout)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.widgets.buttons import PrimaryButton
from database.db_manager import db

class DowntimeReasonDialog(QDialog):
    """
    Diálogo de Seleção de Motivo de Parada (Sovereign Operator Overlay).
    Refinado com UX Industrial: categorização cromática e feedback tátil.
    """
    reason_selected = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowState(Qt.WindowFullScreen)
        self.setObjectName("DowntimeOverlay")
        self._setup_ui()

    def _setup_ui(self):
        # Fundo com profundidade orgânica (transparência 0.85)
        self.setStyleSheet("""
            QDialog#DowntimeOverlay {
                background-color: rgba(0, 42, 77, 0.85); 
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 80, 80, 80)
        main_layout.setSpacing(50)

        # --- Header (Editorial Layer) ---
        header = QVBoxLayout()
        header.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel("SELECIONE O MOTIVO")
        lbl_title.setObjectName("DisplayLarge")
        lbl_title.setStyleSheet("color: #ffffff; font-size: 56px; letter-spacing: -3px;")
        header.addWidget(lbl_title)
        
        soul_bar = QFrame()
        soul_bar.setFixedSize(160, 8)
        soul_bar.setStyleSheet("background-color: #8aacd8; border-radius: 4px;")
        header.addWidget(soul_bar, 0, Qt.AlignCenter)
        
        main_layout.addLayout(header)

        # --- Reasons Grid ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(30) # Aumento de segurança para touch
        
        reasons = db.fetch_all("SELECT * FROM downtime_reasons WHERE is_manual = 1")
        
        row, col = 0, 0
        for reason in reasons:
            # Lógica de Categorização (UX: Scannability)
            border_color = "#8aacd8" # Padrão Operacional
            if "MANUTENÇÃO" in reason['description'].upper():
                border_color = "#ff9800" # Laranja Industrial
            elif "LIMPEZA" in reason['description'].upper():
                border_color = "#4caf50" # Verde Organização
            
            btn = PrimaryButton(reason['description'])
            btn.setMinimumHeight(140)
            btn.setStyleSheet(f"""
                QPushButton#PrimaryButton {{
                    background-color: #ffffff;
                    color: #002a4d;
                    font-size: 22px;
                    border: 4px solid {border_color};
                    border-radius: 12px;
                }}
                QPushButton#PrimaryButton:pressed {{
                    background-color: {border_color};
                    color: #ffffff;
                }}
            """)
            
            btn.clicked.connect(lambda checked=False, r=reason, b=btn: self._on_reason_clicked(r, b))
            
            grid.addWidget(btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # --- Footer ---
        footer = QHBoxLayout()
        btn_cancel = PrimaryButton("RETORNAR AO DASHBOARD")
        btn_cancel.setFixedWidth(400)
        btn_cancel.setStyleSheet("""
            background-color: transparent; 
            color: #ffffff; 
            border: 2px solid rgba(255,255,255,0.4);
            font-size: 14px;
        """)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel, 0, Qt.AlignCenter)
        
        main_layout.addLayout(footer)

    def _on_reason_clicked(self, reason_data, button):
        """Feedback tátil: pequeno delay para o operador ver o clique."""
        # Visual feedback já é dado pelo :pressed no QSS, mas o delay garante percepção
        QTimer.singleShot(150, lambda: self._finalize_selection(reason_data))

    def _finalize_selection(self, reason_data):
        self.reason_selected.emit(reason_data['id'], reason_data['description'])
        self.accept()

