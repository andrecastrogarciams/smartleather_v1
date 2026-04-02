import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from dotenv import load_dotenv

# Adiciona o diretório src ao path para imports funcionarem corretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.views.login_view import LoginView
from ui.views.op_start_view import OPStartView
from ui.views.dashboard_view import DashboardView
from core.production_manager import production_manager
from core.downtime_manager import downtime_manager
from core.state_manager import state_manager
from core.sync_manager import sync_manager

# Carrega variáveis de ambiente
load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLeather v1 — Controle de Produção")
        self.resize(1024, 600) # Resolução para Dashboard

        # QStackedWidget para gerenciar múltiplas telas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Inicializa as views
        self._init_views()
        # Conecta os sinais do Core Engine à UI
        self._connect_core_signals()
        
        # Inicia o serviço de sincronização
        sync_manager.start()

    def _init_views(self):
        # ... (restante do _init_views permanece igual)
        # View de Login
        self.login_view = LoginView()
        self.login_view.login_successful.connect(self._on_login_success)
        self.stacked_widget.addWidget(self.login_view)

        # View de Início de OP (UI-3)
        self.op_start_view = OPStartView()
        self.op_start_view.op_started.connect(self._on_op_started)
        self.op_start_view.logout_requested.connect(self._on_logout)
        self.stacked_widget.addWidget(self.op_start_view)

        # View de Dashboard (UI-4)
        self.dashboard_view = DashboardView()
        self.dashboard_view.downtime_started.connect(self._on_downtime_started)
        self.dashboard_view.downtime_ended.connect(self._on_downtime_ended)
        self.dashboard_view.finish_requested.connect(self._on_finish_op)
        self.stacked_widget.addWidget(self.dashboard_view)

        # Exibe a tela de login inicialmente
        self.stacked_widget.setCurrentWidget(self.login_view)

    def _connect_core_signals(self):
        """Conecta eventos do backend diretamente à DashboardView."""
        production_manager.pulse_recorded.connect(self.dashboard_view.update_production)
        production_manager.buffer_updated.connect(self.dashboard_view.update_buffer)
        # Sincronização e Rede
        sync_manager.network_status_changed.connect(self._on_network_status_changed)

    def _on_network_status_changed(self, is_online):
        """Atualiza indicador visual de rede no Dashboard."""
        status_text = "● NETWORK: ONLINE" if is_online else "○ NETWORK: OFFLINE"
        color = "#006633" if is_online else "#ba1a1a"
        self.dashboard_view.lbl_network.setText(status_text)
        self.dashboard_view.lbl_network.setStyleSheet(f"color: {color};")

    def _on_login_success(self, user_id):
        print(f"[MainApp] User {user_id} logged in. Routing to OP Start...")
        self._current_user = "Operador Padrão" # Mock
        self.op_start_view.set_user(self._current_user)
        self.stacked_widget.setCurrentWidget(self.op_start_view)

    def _on_logout(self):
        print("[MainApp] Logout requested.")
        self.stacked_widget.setCurrentWidget(self.login_view)

    def _on_op_started(self, op_data):
        print(f"[MainApp] OP {op_data['numero']} started. Routing to Dashboard...")
        state_manager.start_op(op_data['numero']) # Ativa no StateManager
        self.dashboard_view.set_op_data(op_data, self._current_user)
        self.stacked_widget.setCurrentWidget(self.dashboard_view)

    def _on_downtime_started(self, reason_id, description):
        """Inicia evento de parada no Core."""
        downtime_manager.start_downtime(reason_id, downtime_type='manual')

    def _on_downtime_ended(self, count_buffer_items):
        """Finaliza parada e processa buffer."""
        downtime_uuid = downtime_manager.current_downtime_uuid
        downtime_manager.end_downtime()
        production_manager.process_buffer(downtime_uuid, contabilizar=count_buffer_items)
        state_manager.resume_production()

    def _on_finish_op(self):
        print("[MainApp] OP finished. Returning to OP Start...")
        state_manager.finish_op()
        self.stacked_widget.setCurrentWidget(self.op_start_view)

def load_theme(app: QApplication):
    """Carrega o arquivo QSS com o Design System."""
    theme_path = os.path.join(os.path.dirname(__file__), "ui", "assets", "style.qss")
    try:
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Aviso: Arquivo de tema não encontrado em {theme_path}")

def main():
    app = QApplication(sys.argv)
    load_theme(app)
    
    window = MainWindow()
    window.show() # Para modo fullscreen use window.showFullScreen() no RPI
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
