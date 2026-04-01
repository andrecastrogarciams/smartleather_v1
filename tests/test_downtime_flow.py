import sys
import os
import time
import uuid
from PySide6.QtCore import QCoreApplication, QTimer

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Ajusta o timeout para o teste (2 segundos)
os.environ["DOWNTIME_TIMEOUT"] = "2"

from database.db_manager import db
from core.state_manager import state_manager, LineState
from core.production_manager import production_manager
from core.downtime_manager import downtime_manager
from hardware.gpio_manager import gpio_manager

class DowntimeTester:
    def __init__(self, app):
        self.app = app
        self.op_number = f"OP-DOWNTIME-{uuid.uuid4().hex[:4].upper()}"
        self.test_step = 1

    def run(self):
        print(f"=== Iniciando Teste de Parada Automática: {self.op_number} ===")
        
        # 1. Criar OP e Iniciar Produção
        print("Passo 1: Criando OP e iniciando produção...")
        db.execute_query(
            "INSERT INTO production_orders (op_number, product_description) VALUES (?, ?)",
            (self.op_number, "Teste de Downtime"),
            commit=True
        )
        state_manager.start_op(self.op_number)
        print(f"Estado inicial: {state_manager.current_state.name}")

        # 2. Agendar verificação de Timeout (após 3 segundos)
        QTimer.singleShot(3000, self.check_timeout)

    def check_timeout(self):
        print("\nPasso 2: Verificando se entrou em DOWNTIME por inatividade...")
        print(f"Estado atual: {state_manager.current_state.name}")
        
        if state_manager.current_state == LineState.DOWNTIME:
            print("✅ Sucesso: Entrou em Parada Automática.")
            
            # Verificar no banco
            downtime = db.fetch_one(
                "SELECT * FROM downtime_events WHERE downtime_type = 'automatic' ORDER BY start_timestamp DESC LIMIT 1"
            )
            if downtime:
                print(f"Registro de parada encontrado: {downtime['uuid']} em {downtime['start_timestamp']}")
            
            # 3. Simular pulso para retomar
            print("\nPasso 3: Simulando pulso para retomar produção...")
            gpio_manager.simulate_pulse()
            
            # Agendar verificação de retomada (após 1 segundo)
            QTimer.singleShot(1000, self.check_resume)
        else:
            print("❌ Falha: Não entrou em DOWNTIME após o tempo limite.")
            self.app.quit()

    def check_resume(self):
        print(f"Estado após pulso: {state_manager.current_state.name}")
        
        if state_manager.current_state == LineState.PRODUCTION:
            print("✅ Sucesso: Retomou produção automaticamente pelo pulso.")
            
            # Verificar se fechou a parada no banco
            downtime = db.fetch_one(
                "SELECT end_timestamp FROM downtime_events ORDER BY start_timestamp DESC LIMIT 1"
            )
            if downtime and downtime['end_timestamp']:
                print(f"✅ Registro de parada fechado com sucesso: {downtime['end_timestamp']}")
                print("\n🎉 TESTE DE PARADA AUTOMÁTICA CONCLUÍDO COM SUCESSO!")
            else:
                print("❌ Falha: Evento de parada não foi fechado no banco.")
        else:
            print("❌ Falha: Não voltou para PRODUCTION após o pulso.")
        
        self.app.quit()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    tester = DowntimeTester(app)
    QTimer.singleShot(100, tester.run)
    sys.exit(app.exec())
