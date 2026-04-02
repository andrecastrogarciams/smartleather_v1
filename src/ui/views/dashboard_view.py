from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                                 QLabel, QSpacerItem, QSizePolicy, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.widgets.buttons import PrimaryButton
from ui.widgets.cards import ProductionCard
from ui.widgets.modals import DowntimeReasonDialog

class DashboardView(QWidget):
    """
    Dashboard de Produção em Tempo Real (UI-4).
    Exibe status da linha, contador de peças e gestão de paradas.
    """
    stop_requested = Signal() 
    downtime_started = Signal(int, str) 
    downtime_ended = Signal(bool) # Emitido ao encerrar: True=Contabilizar, False=Ignorar
    finish_requested = Signal() 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardView")
        self._setup_ui()
        self._op_data = {}
        self._buffer_count = 0

    def _setup_ui(self):
        # ... (Top Bar e Main Area permanecem iguais)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(24)

        # --- Top Bar (Contexto Operacional) ---
        top_bar = QHBoxLayout()
        context_info = QVBoxLayout()
        self.lbl_station = QLabel("STATION: SETOR 01 - LINHA 01")
        self.lbl_station.setObjectName("IndustrialLabel")
        context_info.addWidget(self.lbl_station)
        self.lbl_operator = QLabel("OPERADOR: ---")
        self.lbl_operator.setObjectName("IndustrialLabel")
        context_info.addWidget(self.lbl_operator)
        top_bar.addLayout(context_info)
        top_bar.addStretch()
        status_info = QVBoxLayout()
        self.lbl_shift = QLabel("TURNO: MANHÃ (06:00 - 14:00)")
        self.lbl_shift.setObjectName("IndustrialLabel")
        self.lbl_shift.setAlignment(Qt.AlignRight)
        status_info.addWidget(self.lbl_shift)
        self.lbl_network = QLabel("● NETWORK: ONLINE")
        self.lbl_network.setObjectName("IndustrialLabel")
        self.lbl_network.setStyleSheet("color: #006633;") 
        self.lbl_network.setAlignment(Qt.AlignRight)
        status_info.addWidget(self.lbl_network)
        top_bar.addLayout(status_info)
        main_layout.addLayout(top_bar)

        # --- Main production Area ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(32)
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
        left_col.addWidget(self.op_card)
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
        right_col = QVBoxLayout()
        self.counter_card = ProductionCard()
        self.counter_card.setStyleSheet("background-color: #002a4d;") 
        counter_layout = self.counter_card.layout
        counter_layout.setAlignment(Qt.AlignCenter)
        lbl_total_title = QLabel("PRODUÇÃO TOTAL")
        lbl_total_title.setObjectName("IndustrialLabel")
        lbl_total_title.setStyleSheet("color: #e3f0f8;")
        counter_layout.addWidget(lbl_total_title)
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

        # --- Buffer Alert Section (Hidden by default) ---
        self.buffer_widget = QFrame()
        self.buffer_widget.setObjectName("BufferAlert")
        self.buffer_widget.setStyleSheet("""
            QFrame#BufferAlert {
                background-color: #fffbfe;
                border: 2px solid #ba1a1a;
                border-radius: 8px;
            }
        """)
        self.buffer_widget.setMinimumHeight(80)
        buffer_layout = QHBoxLayout(self.buffer_widget)
        
        self.lbl_buffer_msg = QLabel("⚠ RECEBIDO 0 ITENS DURANTE A PARADA.")
        self.lbl_buffer_msg.setStyleSheet("color: #ba1a1a; font-weight: 900; font-size: 16px;")
        buffer_layout.addWidget(self.lbl_buffer_msg)
        buffer_layout.addStretch()
        
        self.btn_buffer_count = QPushButton("CONTABILIZAR")
        self.btn_buffer_count.setStyleSheet("background-color: #006633; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px;")
        self.btn_buffer_count.clicked.connect(lambda: self._handle_buffer_decision(True))
        buffer_layout.addWidget(self.btn_buffer_count)
        
        self.btn_buffer_ignore = QPushButton("IGNORAR")
        self.btn_buffer_ignore.setStyleSheet("background-color: #73777f; color: white; padding: 10px 20px; font-weight: bold; border-radius: 4px;")
        self.btn_buffer_ignore.clicked.connect(lambda: self._handle_buffer_decision(False))
        buffer_layout.addWidget(self.btn_buffer_ignore)
        
        self.buffer_widget.hide()
        main_layout.addWidget(self.buffer_widget)

        # --- Action Bar ---
        self.action_bar = QHBoxLayout()
        self.action_bar.setSpacing(20)
        
        self.btn_stop = PrimaryButton("REGISTRAR PARADA")
        self.btn_stop.setStyleSheet("background-color: #ba1a1a; color: #ffffff;") 
        self.btn_stop.clicked.connect(self._handle_stop)
        self.action_bar.addWidget(self.btn_stop, 1)
        
        self.btn_finish = PrimaryButton("FINALIZAR ORDEM")
        self.btn_finish.clicked.connect(self._handle_finish)
        self.action_bar.addWidget(self.btn_finish, 1)
        
        main_layout.addLayout(self.action_bar)

        # Adiciona um botão de "RETOMAR PRODUÇÃO" (escondido inicialmente)
        self.btn_resume = PrimaryButton("RETOMAR PRODUÇÃO")
        self.btn_resume.setStyleSheet("background-color: #006633; color: #ffffff;")
        self.btn_resume.clicked.connect(self._handle_resume_request)
        self.btn_resume.hide()
        self.action_bar.addWidget(self.btn_resume, 1)

    def set_op_data(self, op_data, operator_name="Operador Padrão"):
        self._op_data = op_data
        self.lbl_operator.setText(f"OPERADOR: {operator_name.upper()}")
        self.lbl_op_num.setText(op_data.get("numero", "N/D"))
        self.lbl_product.setText(op_data.get("produto", "N/D").upper())
        self.lbl_deriv.setText(op_data.get("derivacao", "N/D").upper())
        self.lbl_prev_val.setText(op_data.get("previsto", "0"))
        self.update_production(0)

    def update_production(self, count):
        self.lbl_count.setText(f"{count:04d}")

    def update_buffer(self, count):
        """Atualiza a contagem do buffer visual."""
        self._buffer_count = count
        if count > 0:
            self.lbl_buffer_msg.setText(f"⚠ RECEBIDO {count} ITENS DURANTE A PARADA.")
            if self.btn_resume.isVisible(): # Só mostra decisão se estiver tentando retomar
                self.buffer_widget.show()
        else:
            self.buffer_widget.hide()

    def _handle_stop(self):
        dialog = DowntimeReasonDialog(self)
        dialog.reason_selected.connect(self._on_reason_confirmed)
        dialog.exec()

    def _on_reason_confirmed(self, reason_id, description):
        self.lbl_status_value.setText(f"PARADA: {description}")
        self.lbl_status_value.setStyleSheet("color: #ba1a1a;")
        self.btn_stop.hide()
        self.btn_finish.hide()
        self.btn_resume.show()
        self.downtime_started.emit(reason_id, description)

    def _handle_resume_request(self):
        """Inicia o processo de retomar produção."""
        if self._buffer_count > 0:
            self.buffer_widget.show() # Força o operador a decidir
        else:
            self._finalize_resume(False) # Retoma sem buffer

    def _handle_buffer_decision(self, count_items):
        """Processa a decisão do buffer e retoma."""
        self._finalize_resume(count_items)

    def _finalize_resume(self, count_items):
        self.lbl_status_value.setText("EM PRODUÇÃO")
        self.lbl_status_value.setStyleSheet("color: #002a4d;")
        self.btn_resume.hide()
        self.buffer_widget.hide()
        self.btn_stop.show()
        self.btn_finish.show()
        self.downtime_ended.emit(count_items)

    def _handle_finish(self):
        self.finish_requested.emit()
