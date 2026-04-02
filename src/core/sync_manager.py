import threading
import time
import mysql.connector
from mysql.connector import Error
from database.db_manager import db
from utils.config import config
from PySide6.QtCore import QObject, Signal

class SyncManager(QObject):
    """
    Gerencia a sincronização de dados entre SQLite local e MySQL Central.
    Opera em background (thread separada).
    """
    network_status_changed = Signal(bool) # True se Online, False se Offline

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._is_online = False
        self._sync_thread = None
        self._lock = threading.Lock()

    def start(self):
        """Inicia o serviço de sincronização."""
        if not self._is_running:
            self._is_running = True
            self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self._sync_thread.start()
            print("[SyncManager] Service started.")

    def stop(self):
        """Para o serviço de sincronização."""
        self._is_running = False

    def _get_mysql_connection(self):
        """Tenta estabelecer conexão com o MySQL Central."""
        try:
            conn = mysql.connector.connect(
                host=config.MYSQL_HOST,
                port=config.MYSQL_PORT,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASS,
                database=config.MYSQL_DB,
                connect_timeout=5
            )
            return conn
        except Error as e:
            # print(f"[SyncManager] Connection error: {e}")
            return None

    def _sync_loop(self):
        """Loop principal de sincronização."""
        while self._is_running:
            conn_central = self._get_mysql_connection()
            
            new_status = conn_central is not None
            if new_status != self._is_online:
                self._is_online = new_status
                self.network_status_changed.emit(self._is_online)
                print(f"[SyncManager] Network status: {'ONLINE' if self._is_online else 'OFFLINE'}")

            if self._is_online:
                try:
                    self._sync_production_events(conn_central)
                    self._sync_downtime_events(conn_central)
                except Exception as e:
                    print(f"[SyncManager] Sync error: {e}")
                finally:
                    if conn_central.is_connected():
                        conn_central.close()
            
            # Intervalo entre tentativas de sync
            time.sleep(30)

    def _sync_production_events(self, conn_central):
        """Sincroniza eventos de produção pendentes."""
        pending_events = db.fetch_all("SELECT * FROM production_events WHERE sync_status = 0 LIMIT 100")
        if not pending_events:
            return

        cursor_central = conn_central.cursor()
        
        for event in pending_events:
            try:
                # Query de inserção no central (Idempotente via INSERT IGNORE ou UUID PK)
                query = """
                    INSERT INTO production_events (
                        uuid, device_id, timestamp, op_id, sector_id, line_id, shift_id, user_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE timestamp=timestamp; -- Garante idempotência
                """
                params = (
                    event['uuid'], event['device_id'], event['timestamp'],
                    event['op_id'], event['sector_id'], event['line_id'],
                    event['shift_id'], event['user_id']
                )
                
                cursor_central.execute(query, params)
                
                # Se inseriu/validou no central, marca como sync no local
                db.execute_query(
                    "UPDATE production_events SET sync_status = 1 WHERE uuid = ?",
                    (event['uuid'],),
                    commit=True
                )
            except Error as e:
                print(f"[SyncManager] Error syncing production event {event['uuid']}: {e}")
                break # Interrompe o lote atual se houver erro de DB central

        conn_central.commit()
        cursor_central.close()

    def _sync_downtime_events(self, conn_central):
        """Sincroniza eventos de parada pendentes."""
        pending_downtimes = db.fetch_all("SELECT * FROM downtime_events WHERE sync_status = 0 LIMIT 50")
        if not pending_downtimes:
            return

        cursor_central = conn_central.cursor()
        
        for dt in pending_downtimes:
            try:
                query = """
                    INSERT INTO downtime_events (
                        uuid, op_id, sector_id, line_id, start_timestamp, end_timestamp, reason_id, downtime_type, user_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE end_timestamp=VALUES(end_timestamp);
                """
                params = (
                    dt['uuid'], dt['op_id'], dt['sector_id'], dt['line_id'],
                    dt['start_timestamp'], dt['end_timestamp'],
                    dt['reason_id'], dt['downtime_type'], dt['user_id']
                )
                
                cursor_central.execute(query, params)
                
                # Só marca como sincronizado localmente se o evento já estiver fechado (end_timestamp preenchido)
                if dt['end_timestamp']:
                    db.execute_query(
                        "UPDATE downtime_events SET sync_status = 1 WHERE uuid = ?",
                        (dt['uuid'],),
                        commit=True
                    )
            except Error as e:
                print(f"[SyncManager] Error syncing downtime event {dt['uuid']}: {e}")
                break

        conn_central.commit()
        cursor_central.close()

# Instância global
sync_manager = SyncManager()
