from PySide6.QtCore import QObject, Signal, Slot
from enum import Enum, auto
import datetime

class LineState(Enum):
    FREE = auto()        # Linha livre, sem OP ativa
    PRODUCTION = auto()  # Em produção normal
    DOWNTIME = auto()    # Linha parada (manual ou automática)

class StateManager(QObject):
    """
    Gerenciador de Estados da Linha de Produção.
    Controla a transição entre estados e emite sinais para a UI.
    """
    state_changed = Signal(LineState)  # Emitido quando o estado muda
    op_started = Signal(str)           # Emitido quando uma OP inicia (número da OP)
    op_finished = Signal(str)          # Emitido quando uma OP é finalizada

    def __init__(self):
        super().__init__()
        self._current_state = LineState.FREE
        self._active_op = None
        self._start_time = None

    @property
    def current_state(self):
        return self._current_state

    @property
    def active_op(self):
        return self._active_op

    def set_state(self, new_state: LineState):
        """Altera o estado e notifica os ouvintes (UI)."""
        if self._current_state != new_state:
            old_state = self._current_state
            self._current_state = new_state
            print(f"[StateManager] State changed: {old_state.name} -> {new_state.name}")
            self.state_changed.emit(new_state)

    def start_op(self, op_number: str):
        """Inicia uma Ordem de Produção."""
        if self._current_state == LineState.FREE:
            self._active_op = op_number
            self._start_time = datetime.datetime.now()
            self.set_state(LineState.PRODUCTION)
            self.op_started.emit(op_number)
            print(f"[StateManager] OP {op_number} started at {self._start_time}")
            return True
        print(f"[StateManager] Cannot start OP. Current state is {self._current_state.name}")
        return False

    def finish_op(self):
        """Finaliza a OP ativa (requer confirmação no fluxo real)."""
        if self._active_op:
            op_finished = self._active_op
            self._active_op = None
            self._start_time = None
            self.set_state(LineState.FREE)
            self.op_finished.emit(op_finished)
            print(f"[StateManager] OP {op_finished} finished.")
            return True
        return False

    def enter_downtime(self):
        """Entra em estado de parada."""
        if self._current_state == LineState.PRODUCTION:
            self.set_state(LineState.DOWNTIME)
            return True
        return False

    def resume_production(self):
        """Retorna da parada para produção."""
        if self._current_state == LineState.DOWNTIME:
            self.set_state(LineState.PRODUCTION)
            return True
        return False

# Instância global para o núcleo da aplicação
state_manager = StateManager()
