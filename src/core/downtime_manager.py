import uuid
import datetime
from PySide6.QtCore import QObject, QTimer, Slot
from core.state_manager import state_manager, LineState
from database.db_manager import db
from utils.config import config

class DowntimeManager(QObject):
    """
    Monitora a inatividade da linha e dispara paradas automáticas.
    """
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._on_timeout)
        
        # O tempo no .env é em segundos, o QTimer usa milissegundos
        self.timeout_ms = config.DOWNTIME_TIMEOUT * 1000
        
        # Conecta aos sinais do StateManager para saber quando monitorar
        state_manager.state_changed.connect(self._on_state_changed)
        
        self._current_downtime_uuid = None

    @Slot(LineState)
    def _on_state_changed(self, new_state):
        """Ativa ou desativa o timer conforme o estado da linha."""
        if new_state == LineState.PRODUCTION:
            self.reset_timer()
        else:
            self.stop_timer()

    @property
    def current_downtime_uuid(self):
        return self._current_downtime_uuid

    def reset_timer(self):
        """Reinicia a contagem de inatividade (chamado em cada pulso)."""
        if state_manager.current_state == LineState.PRODUCTION:
            self.timer.start(self.timeout_ms)

    def stop_timer(self):
        """Para o monitoramento."""
        self.timer.stop()

    def _on_timeout(self):
        """Acionado quando o tempo de inatividade expira."""
        print(f"[DowntimeManager] Timeout reached! Entering Automatic Downtime...")
        self.start_downtime(reason_id=1, downtime_type='automatic')

    def start_downtime(self, reason_id, downtime_type='manual'):
        """Inicia um evento de parada (manual ou automática)."""
        if state_manager.current_state != LineState.PRODUCTION:
            return False

        # 1. Gera UUID para o evento de parada
        self._current_downtime_uuid = str(uuid.uuid4())
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Recupera info da OP ativa
        op_info = db.fetch_one(
            "SELECT id FROM production_orders WHERE op_number = ? LIMIT 1",
            (state_manager.active_op,)
        )
        
        if not op_info:
            print("[DowntimeManager] Error: No active OP found to link downtime.")
            return False

        # 3. Grava o início da parada no SQLite
        query = """
            INSERT INTO downtime_events (
                uuid, op_id, sector_id, line_id, start_timestamp, reason_id, downtime_type, user_id, sync_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
        """
        params = (
            self._current_downtime_uuid,
            op_info['id'],
            config.SECTOR_ID,
            config.LINE_ID,
            start_time,
            reason_id,
            downtime_type
        )

        try:
            db.execute_query(query, params, commit=True)
            # 4. Altera o estado global para DOWNTIME
            state_manager.enter_downtime()
            print(f"[DowntimeManager] {downtime_type.capitalize()} downtime started: {self._current_downtime_uuid}")
            return True
        except Exception as e:
            print(f"[DowntimeManager] Database Error: {e}")
            return False

    def end_downtime(self):
        """Fecha o evento de parada atual no banco de dados."""
        if self._current_downtime_uuid:
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = "UPDATE downtime_events SET end_timestamp = ? WHERE uuid = ?"
            db.execute_query(query, (end_time, self._current_downtime_uuid), commit=True)
            print(f"[DowntimeManager] Downtime event {self._current_downtime_uuid} closed.")
            self._current_downtime_uuid = None

# Instância global
downtime_manager = DowntimeManager()
