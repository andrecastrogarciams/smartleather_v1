-- Tabela de Perfis (Roles)
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE -- Ex: 'Operador', 'Supervisor', 'Admin'
);

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT NOT NULL UNIQUE, -- Matrícula
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (id)
);

-- Tabela de Turnos
CREATE TABLE IF NOT EXISTS shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

-- Tabela de Motivos de Parada
CREATE TABLE IF NOT EXISTS downtime_reasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    is_manual BOOLEAN DEFAULT TRUE
);

-- Tabela de Ordens de Produção (OP)
CREATE TABLE IF NOT EXISTS production_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    op_number TEXT NOT NULL UNIQUE,
    product_code TEXT,
    product_description TEXT,
    variation_code TEXT,
    variation_description TEXT,
    quantity_expected INTEGER,
    status TEXT DEFAULT 'aberta', -- 'aberta', 'pendente_confirmacao', 'finalizada'
    is_contingency BOOLEAN DEFAULT FALSE, -- Identifica se foi aberta offline
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Eventos de Produção (Pulsos)
CREATE TABLE IF NOT EXISTS production_events (
    uuid TEXT PRIMARY KEY, -- UUID v4 para idempotência no MySQL central
    device_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    op_id INTEGER NOT NULL,
    sector_id TEXT NOT NULL,
    line_id TEXT NOT NULL,
    shift_id INTEGER,
    user_id INTEGER NOT NULL,
    sync_status INTEGER DEFAULT 0, -- 0: pendente, 1: sincronizado
    FOREIGN KEY (op_id) REFERENCES production_orders (id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (shift_id) REFERENCES shifts (id)
);

-- Tabela de Eventos de Parada (Downtime)
CREATE TABLE IF NOT EXISTS downtime_events (
    uuid TEXT PRIMARY KEY,
    op_id INTEGER NOT NULL,
    sector_id TEXT NOT NULL,
    line_id TEXT NOT NULL,
    start_timestamp DATETIME NOT NULL,
    end_timestamp DATETIME,
    reason_id INTEGER,
    downtime_type TEXT NOT NULL, -- 'automatic', 'manual'
    user_id INTEGER NOT NULL,
    sync_status INTEGER DEFAULT 0, -- 0: pendente, 1: sincronizado
    FOREIGN KEY (op_id) REFERENCES production_orders (id),
    FOREIGN KEY (reason_id) REFERENCES downtime_reasons (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Buffer de Pulsos durante Parada Manual
CREATE TABLE IF NOT EXISTS downtime_buffer (
    uuid TEXT PRIMARY KEY,
    downtime_event_uuid TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    processed BOOLEAN DEFAULT FALSE, -- Se já foi contabilizado ou ignorado
    FOREIGN KEY (downtime_event_uuid) REFERENCES downtime_events (uuid)
);

-- Configurações Locais
CREATE TABLE IF NOT EXISTS local_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Inserção de Dados Básicos (Seed)
INSERT OR IGNORE INTO roles (name) VALUES ('Operador'), ('Supervisor'), ('Admin');
INSERT OR IGNORE INTO downtime_reasons (description, is_manual) VALUES ('Parada Automática - Timeout', 0);
