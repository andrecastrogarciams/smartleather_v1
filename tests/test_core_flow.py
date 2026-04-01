import sys
import os
import time
import uuid

# Adiciona o diretório src ao path para permitir imports absolutos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.append(src_path)

# Mock da estrutura de pacotes para evitar ImportError de importações relativas nos módulos src
import database.db_manager as db_manager
import hardware.gpio_manager as gpio_manager
import core.state_manager as state_manager
import core.production_manager as production_manager

from database.db_manager import db
from core.state_manager import state_manager as sm_instance, LineState
from core.production_manager import production_manager as pm_instance
from hardware.gpio_manager import gpio_manager as gm_instance

def run_test():
    print("=== Iniciando Teste de Integração: Fluxo de Produção ===")

    # 1. Preparar o banco de dados (inserir uma OP de teste)
    op_number = f"OP-TEST-{uuid.uuid4().hex[:6].upper()}"
    print(f"1. Criando OP de teste: {op_number}")
    db.execute_query(
        "INSERT INTO production_orders (op_number, product_description, quantity_expected) VALUES (?, ?, ?)",
        (op_number, "Produto de Teste", 100),
        commit=True
    )

    # 2. Iniciar a OP no StateManager
    print("2. Iniciando OP no StateManager...")
    if not sm_instance.start_op(op_number):
        print("Erro ao iniciar OP!")
        return

    print(f"Estado atual: {sm_instance.current_state.name}")

    # 3. Simular pulsos da GPIO
    num_pulses = 3
    print(f"3. Simulando {num_pulses} pulsos de produção...")
    for i in range(num_pulses):
        gm_instance.simulate_pulse()
        time.sleep(0.5) # Aguarda o processamento da thread de banco

    # 4. Verificar se os eventos foram gravados no SQLite
    print("4. Verificando registros no banco de dados...")
    events = db.fetch_all(
        "SELECT pe.uuid, pe.timestamp, po.op_number "
        "FROM production_events pe "
        "JOIN production_orders po ON pe.op_id = po.id "
        "WHERE po.op_number = ?",
        (op_number,)
    )

    print(f"Eventos encontrados: {len(events)}")
    for event in events:
        print(f" - Evento [{event['uuid']}] em {event['timestamp']} para {event['op_number']}")

    # 5. Finalizar a OP
    print("5. Finalizando OP...")
    sm_instance.finish_op()
    print(f"Estado final: {sm_instance.current_state.name}")

    # Validação Final
    if len(events) == num_pulses:
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        print(f"\n❌ FALHA NO TESTE: Esperava {num_pulses} eventos, mas encontrei {len(events)}.")

if __name__ == "__main__":
    run_test()
