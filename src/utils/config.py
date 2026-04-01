import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Carrega as variáveis do arquivo .env
        load_dotenv()

        # Identificação do Dispositivo
        self.DEVICE_ID = os.getenv("DEVICE_ID", "RPI-001")
        self.SECTOR_ID = os.getenv("SECTOR_ID", "SETOR-01")
        self.LINE_ID = os.getenv("LINE_ID", "LINHA-01")

        # Parâmetros de Produção
        self.DOWNTIME_TIMEOUT = int(os.getenv("DOWNTIME_TIMEOUT", 300)) # Default 5 minutos

        # Integração (API de OP)
        self.API_URL = os.getenv("API_URL", "http://localhost:8000/api")
        self.API_KEY = os.getenv("API_KEY", "SL-V1-SECRET-KEY")

        # Banco de Dados
        self.DB_NAME = os.getenv("DB_NAME", "smartleather.db")
        self.MYSQL_CENTRAL_URL = os.getenv("MYSQL_CENTRAL_URL", "")

    def __repr__(self):
        return (f"<Config DEVICE_ID={self.DEVICE_ID} SECTOR={self.SECTOR_ID} "
                f"LINE={self.LINE_ID} TIMEOUT={self.DOWNTIME_TIMEOUT}>")

# Instância global de configuração
config = Config()
