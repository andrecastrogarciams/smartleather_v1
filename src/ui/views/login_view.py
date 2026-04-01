from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QSpacerItem, QSizePolicy, QFrame)
from PySide6.QtCore import Qt, Signal
from ui.widgets.buttons import PrimaryButton
from ui.widgets.inputs import IndustrialInput
from ui.widgets.cards import ProductionCard

class LoginView(QWidget):
    """
    Tela de Autenticação refinada para UX: Sovereign Operator.
    """
    login_successful = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LoginView")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        center_layout = QHBoxLayout()
        center_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Card de Login
        self.login_card = ProductionCard()
        self.login_card.setMinimumWidth(400)
        self.login_card.setMaximumWidth(480)
        
        card_layout = self.login_card.layout

        # --- Top Section (Logo/Editorial) ---
        title_container = QVBoxLayout()
        title_container.setSpacing(12)
        title_container.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel("SMARTLEATHER")
        self.logo_label.setObjectName("DisplayLarge")
        self.logo_label.setAlignment(Qt.AlignCenter)
        title_container.addWidget(self.logo_label)

        # A "Barra de Soul" (Primary Highlight)
        soul_bar = QFrame()
        soul_bar.setFixedSize(48, 4)
        soul_bar.setStyleSheet("background-color: #002a4d; border-radius: 2px;")
        title_container.addWidget(soul_bar, 0, Qt.AlignCenter)
        
        card_layout.addLayout(title_container)
        card_layout.addSpacing(40)

        # --- Form Section ---
        # Matrícula
        mat_label = QLabel("MATRÍCULA")
        mat_label.setObjectName("IndustrialLabel")
        card_layout.addWidget(mat_label)
        
        self.input_matricula = IndustrialInput(placeholder="000000")
        card_layout.addWidget(self.input_matricula)
        
        card_layout.addSpacing(24)

        # Senha
        senha_label = QLabel("SENHA")
        senha_label.setObjectName("IndustrialLabel")
        card_layout.addWidget(senha_label)
        
        self.input_senha = IndustrialInput(placeholder="••••••••", is_password=True)
        card_layout.addWidget(self.input_senha)

        card_layout.addSpacing(40)

        # Botão de Entrar
        self.btn_login = PrimaryButton("ENTRAR")
        self.btn_login.clicked.connect(self._handle_login)
        card_layout.addWidget(self.btn_login)

        # Feedback de Erro
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ba1a1a; font-weight: 900; font-size: 12px; margin-top: 16px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        # --- Footer Section ---
        card_layout.addSpacing(48)
        footer_line = QFrame()
        footer_line.setFrameShape(QFrame.HLine)
        footer_line.setStyleSheet("color: #e3f0f8;") # Surface Container
        card_layout.addWidget(footer_line)

        footer_layout = QHBoxLayout()
        version_label = QLabel("VERSION: v1.0.0-alpha")
        version_label.setStyleSheet("font-size: 10px; color: #73777f; font-weight: bold;")
        footer_layout.addWidget(version_label)
        
        level_label = QLabel("STATION: OPS ACCESS")
        level_label.setStyleSheet("font-size: 10px; color: #73777f; font-weight: bold;")
        footer_layout.addWidget(level_label, 0, Qt.AlignRight)
        
        card_layout.addLayout(footer_layout)

        center_layout.addWidget(self.login_card)
        center_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(center_layout)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _handle_login(self):
        """Validação inicial."""
        matricula = self.input_matricula.text().strip()
        senha = self.input_senha.text().strip()

        if matricula == "123" and senha == "123":
            self.error_label.hide()
            self.login_card.setObjectName("ProductionCard") # Reseta estilo de erro se houver
            self.login_card.setStyle(self.login_card.style()) # Força refresh de estilo
            self.login_successful.emit(1)
        else:
            self.show_error("CREDENCIAIS INVÁLIDAS")

    def show_error(self, message):
        """Exibe erro com o status de intervenção visual."""
        self.error_label.setText(message)
        self.error_label.show()
        # "Intervention State"
        self.login_card.setObjectName("ErrorCard")
        self.login_card.setStyle(self.login_card.style()) # Força refresh de estilo
