import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from dotenv import load_dotenv

# Adiciona o diretório src ao path para imports funcionarem corretamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.views.login_view import LoginView
from ui.views.op_start_view import OPStartView

# Carrega variáveis de ambiente
load_dotenv()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartLeather v1 — Controle de Produção")
        self.resize(1024, 600) # Resolução maior para melhor visualização do dashboard depois

        # QStackedWidget para gerenciar múltiplas telas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Inicializa as views
        self._init_views()

    def _init_views(self):
        # View de Login
        self.login_view = LoginView()
        self.login_view.login_successful.connect(self._on_login_success)
        self.stacked_widget.addWidget(self.login_view)

        # View de Início de OP (UI-3)
        self.op_start_view = OPStartView()
        self.op_start_view.op_started.connect(self._on_op_started)
        self.stacked_widget.addWidget(self.op_start_view)

        # Exibe a tela de login inicialmente
        self.stacked_widget.setCurrentWidget(self.login_view)

    def _on_login_success(self, user_id):
        print(f"[MainApp] User {user_id} logged in. Routing to OP Start...")
        # Simula obtenção do nome do usuário (virá do DB futuramente)
        self.op_start_view.set_user("Operador Padrão")
        self.stacked_widget.setCurrentWidget(self.op_start_view)

    def _on_op_started(self, op_data):
        print(f"[MainApp] OP {op_data['numero']} started. Routing to Dashboard...")
        # TODO: Implementar e rotear para Dashboard (UI-4)
        pass

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
