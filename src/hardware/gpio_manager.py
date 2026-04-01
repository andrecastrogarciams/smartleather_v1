import sys
import platform

# Detecta se estamos rodando em um Raspberry Pi (Linux)
try:
    if platform.system() == "Linux":
        import RPi.GPIO as GPIO
        IS_MOCK = False
    else:
        from hardware.gpio_mock import GPIO
        IS_MOCK = True
except ImportError:
    from hardware.gpio_mock import GPIO
    IS_MOCK = True

class GPIOManager:
    """Gerenciador de GPIO centralizado."""
    
    def __init__(self, pin=18): # Pino 18 como padrão para pulso de produção
        self.pin = pin
        self._setup_gpio()

    def _setup_gpio(self):
        """Configura o pino de entrada de pulso."""
        try:
            GPIO.setmode(GPIO.BCM)
            # Configuração com Pull-Down: o pulso é detectado na subida (RISING)
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        except Exception as e:
            print(f"[GPIO Manager] Error during setup: {e}")

    def add_pulse_callback(self, callback):
        """Registra a função que será chamada em cada pulso detectado."""
        try:
            GPIO.add_event_detect(
                self.pin, 
                GPIO.RISING, 
                callback=callback, 
                bouncetime=200 # Anti-debounce de 200ms
            )
            print(f"[GPIO Manager] Callback registered on pin {self.pin}")
        except Exception as e:
            print(f"[GPIO Manager] Error adding event detector: {e}")

    def simulate_pulse(self):
        """Dispara um pulso manualmente (apenas se estiver em modo MOCK)."""
        if IS_MOCK:
            GPIO.simulate_pulse(self.pin)
        else:
            print("[GPIO Manager] Simulation ignored on real hardware.")

    def cleanup(self):
        """Libera os recursos da GPIO."""
        GPIO.cleanup()

# Instância global do gerenciador
gpio_manager = GPIOManager()
