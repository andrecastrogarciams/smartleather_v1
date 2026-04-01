import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="smartleather.db"):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        """Retorna uma conexão com o banco de dados SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        return conn

    def _initialize_db(self):
        """Lê o arquivo de schema e inicializa o banco de dados se não existir."""
        # Se o banco já existe, verificamos se as tabelas estão lá (simplificado para MVP)
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        
        if not os.path.exists(schema_path):
            print(f"Erro: Arquivo de schema não encontrado em {schema_path}")
            return

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        try:
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
            print("Banco de dados inicializado com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")

    def execute_query(self, query, params=(), commit=False):
        """Executa uma query (INSERT, UPDATE, DELETE)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                return cursor
        except sqlite3.Error as e:
            print(f"Erro na execução da query: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Retorna todos os registros de uma consulta."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro na consulta: {e}")
            return []

    def fetch_one(self, query, params=()):
        """Retorna um único registro de uma consulta."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Erro na consulta: {e}")
            return None

# Instância global para uso no app
db = DatabaseManager()
