import uuid
import datetime
import threading
from core.state_manager import state_manager, LineState
from hardware.gpio_manager import gpio_manager
from database.db_manager import db
from utils.config import config

class ProductionManager:
    """
    Gerencia o fluxo de produção: captura pulsos da GPIO e salva no Banco de Dados.
    """
    def __init__(self):
        self._setup_listeners()
        self._current_user_id = 1 # TODO: Integrar com Sessão/Login (Default Admin/Op inicial)
        self._current_shift_id = None # TODO: Integrar com Gerenciador de Turnos

    def _setup_listeners(self):
        """Registra o callback no gerenciador de GPIO."""
        gpio_manager.add_pulse_callback(self._on_pulse_received)

    def _on_pulse_received(self, pin):
        """Callback acionado em cada pulso da GPIO."""
        # Só contabiliza se o estado for PRODUCTION
        if state_manager.current_state == LineState.PRODUCTION:
            # Executa a persistência em uma thread separada para não travar a GPIO
            threading.Thread(target=self._record_production_event, daemon=True).start()
        elif state_manager.current_state == LineState.DOWNTIME:
            print(f"[ProductionManager] Pulse ignored: Line is in DOWNTIME")
            # TODO: Implementar Buffer para Parada Manual (Story CORE-4)
        else:
            print(f"[ProductionManager] Pulse ignored: Line is FREE")

    def _record_production_event(self):
        """Persiste o evento de produção no SQLite."""
        event_uuid = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Recupera o ID da OP ativa (precisamos do ID interno do banco, não apenas o número)
        op_info = db.fetch_one(
            "SELECT id FROM production_orders WHERE op_number = ? LIMIT 1",
            (state_manager.active_op,)
        )
        
        if not op_info:
            print(f"[ProductionManager] Error: Active OP {state_manager.active_op} not found in database.")
            return

        op_id = op_info['id']

        query = """
            INSERT INTO production_events (
                uuid, device_id, timestamp, op_id, sector_id, line_id, shift_id, user_id, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """
        params = (
            event_uuid,
            config.DEVICE_ID,
            timestamp,
            op_id,
            config.SECTOR_ID,
            config.LINE_ID,
            self._current_shift_id,
            self._current_user_id
        )

        try:
            db.execute_query(query, params, commit=True)
            print(f"[ProductionManager] Event recorded: {event_uuid} for OP {state_manager.active_op}")
        except Exception as e:
            print(f"[ProductionManager] Database Error: {e}")

# Instância global
production_manager = ProductionManager()
