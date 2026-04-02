from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QSpacerItem, QSizePolicy, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.widgets.buttons import PrimaryButton
from ui.widgets.cards import ProductionCard

class DashboardView(QWidget):
    """
    Dashboard de Produção em Tempo Real (UI-4).
    Exibe status da linha, contador de peças e gestão de paradas.
    """
    stop_requested = Signal() # Solicitação de parada manual
    finish_requested = Signal() # Solicitação de finalização de OP

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardView")
        self._setup_ui()
        self._op_data = {}

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # --- Top Bar (Contexto Operacional) ---
        top_bar = QHBoxLayout()
        
        # Info do Operador & Posto
        context_info = QVBoxLayout()
        self.lbl_station = QLabel("STATION: SETOR 01 - LINHA 01")
        self.lbl_station.setObjectName("IndustrialLabel")
        context_info.addWidget(self.lbl_station)
        
        self.lbl_operator = QLabel("OPERADOR: ---")
        self.lbl_operator.setObjectName("IndustrialLabel")
        context_info.addWidget(self.lbl_operator)
        
        top_bar.addLayout(context_info)
        top_bar.addStretch()
        
        # Status da Conexão & Turno
        status_info = QVBoxLayout()
        self.lbl_shift = QLabel("TURNO: MANHÃ (06:00 - 14:00)")
        self.lbl_shift.setObjectName("IndustrialLabel")
        self.lbl_shift.setAlignment(Qt.AlignRight)
        status_info.addWidget(self.lbl_shift)
        
        self.lbl_network = QLabel("● NETWORK: ONLINE")
        self.lbl_network.setObjectName("IndustrialLabel")
        self.lbl_network.setStyleSheet("color: #006633;") # Sucesso/Online
        self.lbl_network.setAlignment(Qt.AlignRight)
        status_info.addWidget(self.lbl_network)
        
        top_bar.addLayout(status_info)
        main_layout.addLayout(top_bar)

        # --- Main production Area ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(32)

        # Left Column: Info da OP & Produto
        left_col = QVBoxLayout()
        
        self.op_card = ProductionCard()
        op_layout = self.op_card.layout
        
        lbl_op_title = QLabel("ORDEM DE PRODUÇÃO")
        lbl_op_title.setObjectName("IndustrialLabel")
        op_layout.addWidget(lbl_op_title)
        
        self.lbl_op_num = QLabel("OP-000000")
        self.lbl_op_num.setObjectName("DisplayLarge")
        op_layout.addWidget(self.lbl_op_num)
        
        op_layout.addSpacing(20)
        
        lbl_prod_title = QLabel("PRODUTO / DERIVAÇÃO")
        lbl_prod_title.setObjectName("IndustrialLabel")
        op_layout.addWidget(lbl_prod_title)
        
        self.lbl_product = QLabel("PRODUTO NÃO CARREGADO")
        self.lbl_product.setObjectName("DisplayLarge")
        self.lbl_product.setStyleSheet("font-size: 24px;")
        op_layout.addWidget(self.lbl_product)
        
        self.lbl_deriv = QLabel("---")
        self.lbl_deriv.setStyleSheet("font-size: 18px; color: #43474e; font-weight: bold;")
        op_layout.addWidget(self.lbl_deriv)
        
        left_col.addWidget(self.details_card if hasattr(self, 'details_card') else self.op_card)
        
        # Status da Linha (Visual)
        self.status_card = ProductionCard()
        status_layout = self.status_card.layout
        status_layout.setAlignment(Qt.AlignCenter)
        
        lbl_status_title = QLabel("STATUS DA LINHA")
        lbl_status_title.setObjectName("IndustrialLabel")
        status_layout.addWidget(lbl_status_title)
        
        self.lbl_status_value = QLabel("EM PRODUÇÃO")
        self.lbl_status_value.setObjectName("DisplayLarge")
        self.lbl_status_value.setStyleSheet("color: #002a4d;")
        status_layout.addWidget(self.lbl_status_value)
        
        left_col.addWidget(self.status_card)
        content_layout.addLayout(left_col, 2)

        # Right Column: Contador (The "Sovereign Counter")
        right_col = QVBoxLayout()
        
        self.counter_card = ProductionCard()
        self.counter_card.setStyleSheet("background-color: #002a4d;") # Destaque brutalista
        counter_layout = self.counter_card.layout
        counter_layout.setAlignment(Qt.AlignCenter)
        
        lbl_prod_title = QLabel("PRODUÇÃO TOTAL")
        lbl_prod_title.setObjectName("IndustrialLabel")
        lbl_prod_title.setStyleSheet("color: #e3f0f8;")
        counter_layout.addWidget(lbl_prod_title)
        
        self.lbl_count = QLabel("0000")
        self.lbl_count.setObjectName("DisplayLarge")
        self.lbl_count.setStyleSheet("font-size: 120px; color: #ffffff; letter-spacing: -5px;")
        counter_layout.addWidget(self.lbl_count)
        
        lbl_prev_title = QLabel("PREVISTO")
        lbl_prev_title.setObjectName("IndustrialLabel")
        lbl_prev_title.setStyleSheet("color: #e3f0f8;")
        counter_layout.addWidget(lbl_prev_title)
        
        self.lbl_prev_val = QLabel("0000")
        self.lbl_prev_val.setStyleSheet("font-size: 24px; color: #8aacd8; font-weight: 900;")
        counter_layout.addWidget(self.lbl_prev_val)
        
        right_col.addWidget(self.counter_card)
        content_layout.addLayout(right_col, 3)
        
        main_layout.addLayout(content_layout)

        # --- Action Bar (Sovereign Operator Controls) ---
        action_bar = QHBoxLayout()
        action_bar.setSpacing(20)
        
        self.btn_stop = PrimaryButton("REGISTRAR PARADA")
        self.btn_stop.setStyleSheet("background-color: #ba1a1a; color: #ffffff;") # Red for Stop
        self.btn_stop.clicked.connect(self._handle_stop)
        action_bar.addWidget(self.btn_stop, 1)
        
        self.btn_finish = PrimaryButton("FINALIZAR ORDEM")
        self.btn_finish.clicked.connect(self._handle_finish)
        action_bar.addWidget(self.btn_finish, 1)
        
        main_layout.addLayout(action_bar)

    def set_op_data(self, op_data, operator_name="Operador Padrão"):
        """Atualiza o dashboard com os dados da OP iniciada."""
        self._op_data = op_data
        self.lbl_operator.setText(f"OPERADOR: {operator_name.upper()}")
        self.lbl_op_num.setText(op_data.get("numero", "N/D"))
        self.lbl_product.setText(op_data.get("produto", "N/D").upper())
        self.lbl_deriv.setText(op_data.get("derivacao", "N/D").upper())
        self.lbl_prev_val.setText(op_data.get("previsto", "0"))
        self.lbl_count.setText("0000") # Reseta contador

    def update_production(self, count):
        """Atualiza o contador de produção (será chamado pelo Core Engine)."""
        self.lbl_count.setText(f"{count:04d}")

    def _handle_stop(self):
        print("[Dashboard] Parada solicitada.")
        self.stop_requested.emit()

    def _handle_finish(self):
        print("[Dashboard] Finalização solicitada.")
        self.finish_requested.emit()
