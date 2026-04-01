import sys
import os
import time
import uuid
from PySide6.QtCore import QCoreApplication, QTimer

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from database.db_manager import db
from core.state_manager import state_manager, LineState
from core.production_manager import production_manager
from core.downtime_manager import downtime_manager
from hardware.gpio_manager import gpio_manager

class ManualBufferTester:
    def __init__(self, app):
        self.app = app
        self.op_number = f"OP-BUFFER-{uuid.uuid4().hex[:4].upper()}"

    def run(self):
        print(f"=== Iniciando Teste de Buffer Manual: {self.op_number} ===")
        
        # 1. Preparar OP
        db.execute_query(
            "INSERT INTO production_orders (op_number, product_description) VALUES (?, ?)",
            (self.op_number, "Teste de Buffer"),
            commit=True
        )
        state_manager.start_op(self.op_number)
        print(f"Estado inicial: {state_manager.current_state.name}")

        # 2. Iniciar Parada Manual (Motivo 2 - Ex: Manutenção)
        # Primeiro garantimos que o motivo existe
        db.execute_query("INSERT OR IGNORE INTO downtime_reasons (id, description, is_manual) VALUES (2, 'Manutenção', 1)", commit=True)
        
        print("\nPasso 1: Entrando em Parada Manual...")
        downtime_manager.start_downtime(reason_id=2, downtime_type='manual')
        print(f"Estado atual: {state_manager.current_state.name}")
        self.downtime_uuid = downtime_manager.current_downtime_uuid

        # 3. Simular 2 pulsos durante a parada
        print("\nPasso 2: Simulando 2 pulsos durante a parada manual...")
        gpio_manager.simulate_pulse()
        time.sleep(0.5)
        gpio_manager.simulate_pulse()
        
        # Aguarda gravação no buffer
        QTimer.singleShot(1000, self.check_buffer)

    def check_buffer(self):
        print("\nPasso 3: Verificando se pulsos entraram no buffer...")
        buffer_items = db.fetch_all(
            "SELECT * FROM downtime_buffer WHERE downtime_event_uuid = ?",
            (self.downtime_uuid,)
        )
        print(f"Itens no buffer: {len(buffer_items)}")
        
        if len(buffer_items) == 2:
            print("✅ Sucesso: 2 pulsos encontrados no buffer.")
            
            # 4. Finalizar parada e processar buffer (Contabilizar)
            print("\nPasso 4: Finalizando parada e contabilizando buffer...")
            downtime_manager.end_downtime()
            state_manager.resume_production()
            
            production_manager.process_buffer(self.downtime_uuid, contabilizar=True)
            
            # Aguarda processamento
            QTimer.singleShot(1000, self.final_validation)
        else:
            print(f"❌ Falha: Esperava 2 pulsos no buffer, mas encontrei {len(buffer_items)}.")
            self.app.quit()

    def final_validation(self):
        print("\nPasso 5: Validação Final...")
        
        # Verificar se saíram do buffer
        buffer_count = db.fetch_one(
            "SELECT COUNT(*) as count FROM downtime_buffer WHERE downtime_event_uuid = ?",
            (self.downtime_uuid,)
        )['count']
        
        # Verificar se entraram na produção
        prod_count = db.fetch_one(
            "SELECT COUNT(*) as count FROM production_events pe "
            "JOIN production_orders po ON pe.op_id = po.id "
            "WHERE po.op_number = ?",
            (self.op_number,)
        )['count']

        print(f"Itens restantes no buffer: {buffer_count}")
        print(f"Eventos de produção registrados para esta OP: {prod_count}")

        if buffer_count == 0 and prod_count == 2:
            print("\n✅ TESTE DE BUFFER MANUAL CONCLUÍDO COM SUCESSO!")
        else:
            print("\n❌ FALHA NA VALIDAÇÃO FINAL.")
        
        self.app.quit()

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    tester = ManualBufferTester(app)
    QTimer.singleShot(100, tester.run)
    sys.exit(app.exec())
