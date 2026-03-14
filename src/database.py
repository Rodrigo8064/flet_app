import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'financas.db'

# trocar para esta configuracao antes de buildar para producao
# BASE_DIR = Path(os.getenv("FLET_APP_STORAGE_DATA", Path(__file__).parent.parent))
# DB_PATH  = BASE_DIR / "financas.db"

_conn: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute('PRAGMA journal_mode=WAL')
        _conn.execute('PRAGMA foreign_keys=ON')
    return _conn


def initialize_database() -> None:
    conn = _connect()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL UNIQUE
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            data           TEXT    NOT NULL,
            payment_method TEXT    NOT NULL CHECK(payment_method IN ('Cartão', 'Pix')),
            type           TEXT    NOT NULL CHECK(type IN ('Receita','Despesa')),
            value          REAL    NOT NULL CHECK(value > 0),
            account_id     INTEGER NOT NULL REFERENCES accounts(id),
            category       TEXT    NOT NULL,
            observation    TEXT    DEFAULT ''
        )
    """)

    _seed_accounts(conn)
    _seed_categories(conn)

    conn.commit()


def _seed_accounts(conn: sqlite3.Connection) -> None:
    existe = conn.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]
    if existe == 0:
        patterns = ['Inter', 'Itaú']
        conn.executemany(
            'INSERT INTO accounts (name) VALUES (?)',
            [(c,) for c in patterns],
        )


def _seed_categories(conn: sqlite3.Connection) -> None:
    existe = conn.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
    if existe == 0:
        patterns = [
            'Outros',
        ]
        conn.executemany(
            'INSERT INTO categories (name) VALUES (?)',
            [(c,) for c in patterns],
        )


# ══════════════════════════════════════════════════════════════════════════════
# CARTÕES
# ══════════════════════════════════════════════════════════════════════════════
def list_accounts() -> list[dict]:
    conn = _connect()
    rows = conn.execute('SELECT id, name FROM accounts ORDER BY name').fetchall()
    return [dict(r) for r in rows]


def insert_account(name: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError('O name da conta não pode ser vazio.')
    conn = _connect()
    try:
        cursor = conn.execute('INSERT INTO accounts (name) VALUES (?)', (name,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Conta '{name}' já existe.")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIAS
# ══════════════════════════════════════════════════════════════════════════════
def list_categories() -> list[dict]:
    conn = _connect()
    rows = conn.execute('SELECT id, name FROM categories ORDER BY name').fetchall()
    return [dict(r) for r in rows]


def insert_category(name: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError('O name da categoria não pode ser vazio.')
    conn = _connect()
    try:
        cursor = conn.execute('INSERT INTO categories (name) VALUES (?)', (name,))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Categoria '{name}' já existe.")


# ══════════════════════════════════════════════════════════════════════════════
# MOVIMENTAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
def list_movements() -> list[dict]:
    conn = _connect()
    rows = conn.execute("""
        SELECT
            m.id,
            m.data,
            m.payment_method,
            m.type,
            m.value,
            m.account_id,
            c.name  AS account,
            m.category,
            m.observation
        FROM movements m
        JOIN accounts c ON c.id = m.account_id
        ORDER BY m.data DESC, m.id DESC
    """).fetchall()
    return [dict(r) for r in rows]


def insert_movement(
    data: str,
    payment_method: str,
    m_type: str,
    value: float,
    account_id: int,
    category: str,
    observation: str = '',
) -> int:
    if m_type not in ('Receita', 'Despesa'):
        raise ValueError(f'Tipo inválido: {m_type}')
    if value <= 0:
        raise ValueError('Valor deve ser maior que zero.')

    conn = _connect()
    cursor = conn.execute(
        """
        INSERT INTO movements
            (data, payment_method, type, value, account_id, category, observation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (data, payment_method, m_type, value, account_id, category, observation),
    )
    conn.commit()
    return cursor.lastrowid


def delete_movement(mov_id: int) -> None:
    conn = _connect()
    conn.execute('DELETE FROM movements WHERE id = ?', (mov_id,))
    conn.commit()


def search_movement(mov_id: int) -> dict | None:
    conn = _connect()
    row = conn.execute('SELECT * FROM movements WHERE id = ?', (mov_id,)).fetchone()
    return dict(row) if row else None


def update_movement(
    mov_id: int,
    data: str,
    payment_method: str,
    m_type: str,
    value: float,
    account_id: int,
    category: str,
    observation: str = '',
) -> None:
    if m_type not in ('Receita', 'Despesa'):
        raise ValueError(f'Tipo inválido: {m_type}')
    if value <= 0:
        raise ValueError('Valor deve ser maior que zero.')
    
    conn = _connect()
    conn.execute(
        '''
        UPDATE movements
            SET data           = ?,
                payment_method = ?,
                type           = ?,
                value          = ?,
                account_id     = ?,
                category       = ?,
                observation    = ?
        WHERE id = ?
        ''',
        (data, payment_method, m_type, value, account_id, category, observation, mov_id)
    )
    conn.commit()


def close_databas() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
