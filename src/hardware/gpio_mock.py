import time
import threading

class GPIOMock:
    """Simulador de RPi.GPIO para desenvolvimento em ambientes não-Linux (Windows/Mac)."""
    
    BOARD = "BOARD"
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"
    PUD_UP = "PUD_UP"
    PUD_DOWN = "PUD_DOWN"

    def __init__(self):
        self._callbacks = {}
        self._pins_mode = {}
        self._mode = None

    def setmode(self, mode):
        self._mode = mode
        print(f"[GPIO MOCK] Mode set to {mode}")

    def setup(self, pin, direction, pull_up_down=None):
        self._pins_mode[pin] = direction
        print(f"[GPIO MOCK] Pin {pin} setup as {direction}")

    def add_event_detect(self, pin, edge, callback=None, bouncetime=None):
        """Simula a detecção de eventos em um pino."""
        self._callbacks[pin] = {
            'edge': edge,
            'callback': callback,
            'bouncetime': bouncetime
        }
        print(f"[GPIO MOCK] Event detection added for pin {pin} on {edge} edge")

    def input(self, pin):
        """Simula a leitura de um pino. Sempre retorna 0 por padrão."""
        return 0

    def cleanup(self):
        print("[GPIO MOCK] Cleanup performed")
        self._callbacks.clear()
        self._pins_mode.clear()

    # --- Métodos de Teste (Exclusivos do Mock) ---

    def simulate_pulse(self, pin):
        """Simula o disparo de um pulso em um pino configurado."""
        if pin in self._callbacks:
            callback_info = self._callbacks[pin]
            callback = callback_info['callback']
            if callback:
                # Executa em uma thread separada para não travar a UI/Main Loop
                threading.Thread(target=callback, args=(pin,), daemon=True).start()
                print(f"[GPIO MOCK] Pulse simulated on pin {pin}")
        else:
            print(f"[GPIO MOCK] Warning: No event detector for pin {pin}")

# Instância Singleton para o Mock
GPIO = GPIOMock()
