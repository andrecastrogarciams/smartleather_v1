from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QSpacerItem, QSizePolicy, QFrame, QStackedWidget, QPushButton)
from PySide6.QtCore import Qt, Signal
from ui.widgets.buttons import PrimaryButton
from ui.widgets.inputs import IndustrialInput
from ui.widgets.cards import ProductionCard

class OPStartView(QWidget):
    """
    Tela de Início de Ordem de Produção (UI-3).
    Permite buscar OP via API ou entrada manual em contingência.
    """
    op_started = Signal(dict) # Emite os dados da OP iniciada
    logout_requested = Signal() # Sinal para voltar ao login

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OPStartView")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # --- Header Section ---
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        self.title_label = QLabel("INICIAR OPERAÇÃO")
        self.title_label.setObjectName("DisplayLarge")
        title_container.addWidget(self.title_label)
        
        soul_bar = QFrame()
        soul_bar.setFixedSize(64, 4)
        soul_bar.setStyleSheet("background-color: #002a4d; border-radius: 2px;")
        title_container.addWidget(soul_bar)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Info do Operador & Logout
        user_container = QVBoxLayout()
        self.user_info = QLabel("OPERADOR: CARREGANDO...")
        self.user_info.setObjectName("IndustrialLabel")
        self.user_info.setAlignment(Qt.AlignRight)
        user_container.addWidget(self.user_info)

        self.btn_logout = QPushButton("LOGOUT / SAIR")
        self.btn_logout.setStyleSheet("border: none; color: #ba1a1a; font-weight: 900; font-size: 10px; text-decoration: underline;")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.clicked.connect(self.logout_requested.emit)
        user_container.addWidget(self.btn_logout, 0, Qt.AlignRight)

        header_layout.addLayout(user_container)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # --- Search Section ---
        search_container = QHBoxLayout()
        
        search_box = QVBoxLayout()
        search_label = QLabel("NÚMERO DA OP")
        search_label.setObjectName("IndustrialLabel")
        search_box.addWidget(search_label)
        
        self.input_op = IndustrialInput(placeholder="DIGITE A OP...")
        self.input_op.setMinimumWidth(300)
        self.input_op.returnPressed.connect(self._handle_search) # UX: Busca via Enter
        search_box.addWidget(self.input_op)
        search_container.addLayout(search_box)
        
        self.btn_search = PrimaryButton("BUSCAR")
        self.btn_search.setFixedWidth(150)
        self.btn_search.clicked.connect(self._handle_search)
        search_container.addWidget(self.btn_search, 0, Qt.AlignBottom)
        
        search_container.addStretch()
        main_layout.addLayout(search_container)

        # --- Details Section (The Sovereign Card) ---
        self.details_card = ProductionCard()
        self.details_card.setVisible(False)
        
        card_layout = self.details_card.layout
        card_layout.setContentsMargins(32, 32, 32, 32)
        
        # Grid de detalhes
        details_grid = QHBoxLayout()
        
        def add_info_field(parent_layout, label_text, value_obj_name):
            box = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setObjectName("IndustrialLabel")
            val = QLabel("---")
            val.setObjectName("DisplayLarge")
            val.setStyleSheet("font-size: 24px;") 
            setattr(self, value_obj_name, val)
            box.addWidget(lbl)
            box.addWidget(val)
            parent_layout.addLayout(box)
            parent_layout.addSpacing(40)

        add_info_field(details_grid, "PRODUTO", "val_produto")
        add_info_field(details_grid, "DERIVAÇÃO", "val_derivacao")
        add_info_field(details_grid, "PREVISTO", "val_previsto")
        
        details_grid.addStretch()
        card_layout.addLayout(details_grid)
        card_layout.addSpacing(32)
        
        # Footer do Card com o botão de iniciar
        self.btn_start = PrimaryButton("CONFIRMAR E INICIAR")
        self.btn_start.clicked.connect(self._handle_start)
        card_layout.addWidget(self.btn_start)
        
        main_layout.addWidget(self.details_card)
        
        # Feedback de Erro/Contingência
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

    def set_user(self, name):
        self.user_info.setText(f"OPERADOR: {name.upper()}")

    def _handle_search(self):
        op_num = self.input_op.text().strip()
        if not op_num:
            return

        print(f"[OPStartView] Buscando OP: {op_num}")
        # Reset card style
        self.details_card.setObjectName("ProductionCard")
        self.details_card.setStyle(self.details_card.style())

        # Mock de busca
        if op_num == "999": # Simulação de Erro/Contingência
            self.status_label.setText("⚠️ OP NÃO ENCONTRADA. DESEJA INICIAR EM MODO CONTINGÊNCIA?")
            self.status_label.setStyleSheet("color: #ba1a1a; font-weight: bold; font-size: 14px;")
            
            # Muda card para modo intervenção (error state)
            self.details_card.setObjectName("ErrorCard")
            self.details_card.setStyle(self.details_card.style())
            
            # Permite iniciar mesmo assim (contigência manual)
            self.current_op_data = {
                "numero": op_num,
                "produto": "OP MANUAL (CONTINGÊNCIA)",
                "derivacao": "N/D",
                "previsto": "0"
            }
            self.val_produto.setText(self.current_op_data["produto"])
            self.val_derivacao.setText(self.current_op_data["derivacao"])
            self.val_previsto.setText(self.current_op_data["previsto"])
            self.details_card.setVisible(True)
        else:
            self.current_op_data = {
                "numero": op_num,
                "produto": "COURO BOVINO TOP GRAIN",
                "derivacao": "PRETO FOSCO",
                "previsto": "1,500"
            }
            self.val_produto.setText(self.current_op_data["produto"])
            self.val_derivacao.setText(self.current_op_data["derivacao"])
            self.val_previsto.setText(self.current_op_data["previsto"])
            self.details_card.setVisible(True)
            self.status_label.setText("✅ DADOS OBTIDOS VIA API.")
            self.status_label.setStyleSheet("color: #006633; font-weight: bold; font-size: 14px;")

    def _handle_start(self):
        if hasattr(self, 'current_op_data'):
            print(f"[OPStartView] Iniciando OP: {self.current_op_data['numero']}")
            self.op_started.emit(self.current_op_data)
