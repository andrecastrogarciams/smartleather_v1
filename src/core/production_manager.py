import uuid
import datetime
import threading
from PySide6.QtCore import QObject, Signal
from core.state_manager import state_manager, LineState
from hardware.gpio_manager import gpio_manager
from database.db_manager import db
from utils.config import config
from core.downtime_manager import downtime_manager

class ProductionManager(QObject):
    """
    Gerencia o fluxo de produção: captura pulsos da GPIO e salva no Banco de Dados.
    Refinado para suportar Buffer de Parada Manual.
    """
    pulse_recorded = Signal(int) # Emitido para atualizar UI: contador total
    buffer_updated = Signal(int) # Emitido para atualizar UI: contador de buffer

    def __init__(self):
        super().__init__()
        self._setup_listeners()
        self._current_user_id = 1 
        self._current_shift_id = None 

    def _setup_listeners(self):
        """Registra o callback no gerenciador de GPIO."""
        gpio_manager.add_pulse_callback(self._on_pulse_received)

    def _on_pulse_received(self, pin):
        """Callback acionado em cada pulso da GPIO."""
        if state_manager.current_state == LineState.PRODUCTION:
            downtime_manager.reset_timer()
            threading.Thread(target=self._record_production_event, daemon=True).start()
            
        elif state_manager.current_state == LineState.DOWNTIME:
            # Verifica o tipo de parada atual
            last_downtime = db.fetch_one(
                "SELECT uuid, downtime_type FROM downtime_events WHERE uuid = ?",
                (downtime_manager.current_downtime_uuid,)
            )
            
            if last_downtime and last_downtime['downtime_type'] == 'automatic':
                print("[ProductionManager] Pulse received during Automatic Downtime. Resuming production...")
                downtime_manager.end_downtime()
                state_manager.resume_production()
                threading.Thread(target=self._record_production_event, daemon=True).start()
            else:
                # Se for Manual, envia para o buffer
                print(f"[ProductionManager] Pulse received during Manual Downtime. Adding to buffer.")
                threading.Thread(target=self._add_to_buffer, daemon=True).start()
        else:
            print(f"[ProductionManager] Pulse ignored: Line is FREE")

    def _record_production_event(self, timestamp=None):
        """Persiste o evento de produção no SQLite."""
        event_uuid = str(uuid.uuid4())
        if not timestamp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        op_info = db.fetch_one(
            "SELECT id FROM production_orders WHERE op_number = ? LIMIT 1",
            (state_manager.active_op,)
        )
        
        if not op_info:
            return

        query = """
            INSERT INTO production_events (
                uuid, device_id, timestamp, op_id, sector_id, line_id, shift_id, user_id, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """
        params = (event_uuid, config.DEVICE_ID, timestamp, op_info['id'], 
                  config.SECTOR_ID, config.LINE_ID, self._current_shift_id, self._current_user_id)

        try:
            db.execute_query(query, params, commit=True)
            # Busca contagem total da OP para emitir sinal
            count_data = db.fetch_one(
                "SELECT COUNT(*) as total FROM production_events WHERE op_id = ?",
                (op_info['id'],)
            )
            self.pulse_recorded.emit(count_data['total'])
            print(f"[ProductionManager] [SUCCESS] Event recorded: {event_uuid} | Total: {count_data['total']}")
        except Exception as e:
            print(f"[ProductionManager] [DATABASE ERROR] Failed to record event {event_uuid}: {e}")

    def _add_to_buffer(self):
        """Adiciona um pulso ao buffer de parada manual e notifica a UI."""
        buffer_uuid = str(uuid.uuid4())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        downtime_uuid = downtime_manager.current_downtime_uuid
        
        if not downtime_uuid:
            return

        query = "INSERT INTO downtime_buffer (uuid, downtime_event_uuid, timestamp) VALUES (?, ?, ?)"
        try:
            db.execute_query(query, (buffer_uuid, downtime_uuid, timestamp), commit=True)
            
            # Conta itens no buffer atual para notificar UI
            buffer_data = db.fetch_one(
                "SELECT COUNT(*) as total FROM downtime_buffer WHERE downtime_event_uuid = ? AND processed = 0",
                (downtime_uuid,)
            )
            self.buffer_updated.emit(buffer_data['total'])
            print(f"[ProductionManager] [BUFFER] Pulse added. Total in Buffer: {buffer_data['total']}")
        except Exception as e:
            print(f"[ProductionManager] [BUFFER ERROR] Failed to add pulse to buffer: {e}")

    def process_buffer(self, downtime_uuid, contabilizar=True):
        """
        Processa o buffer de uma parada: contabiliza como produção ou apenas limpa.
        """
        if contabilizar:
            buffer_items = db.fetch_all(
                "SELECT timestamp FROM downtime_buffer WHERE downtime_event_uuid = ? AND processed = 0",
                (downtime_uuid,)
            )
            print(f"[ProductionManager] Processing buffer: {len(buffer_items)} items to record.")
            for item in buffer_items:
                self._record_production_event(timestamp=item['timestamp'])

        # Remove do buffer após processar (para simplificar auditoria local no MVP)
        db.execute_query(
            "DELETE FROM downtime_buffer WHERE downtime_event_uuid = ?", 
            (downtime_uuid,), 
            commit=True
        )
        self.buffer_updated.emit(0) # Reseta contador visual do buffer
        print(f"[ProductionManager] Buffer cleared for downtime {downtime_uuid}")

# Instância global
production_manager = ProductionManager()
