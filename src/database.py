import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'financas.db'

# trocar para esta configuracao antes de buildar para producao
# BASE_DIR = Path(os.getenv("FLET_APP_STORAGE_DATA", Path(__file__).parent.parent))
# DB_PATH  = BASE_DIR / "financas.db"

class _Database:
 
    def __init__(self, path: Path) -> None:
        self._path = path
        self._conn: sqlite3.Connection | None = None
 
    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn
 
    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
 
 
_db = _Database(DB_PATH)


def _rows_to_dicts(rows) -> list[dict]:
    return [dict(r) for r in rows]
 
 
def _seed(conn: sqlite3.Connection, table: str, values: list[str]) -> None:
    exists = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    if exists == 0:
        conn.executemany(
            f"INSERT INTO {table} (name) VALUES (?)",
            [(v,) for v in values],
        )


def initialize_database() -> None:
    conn = _db.conn
 
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
            date           TEXT    NOT NULL CHECK(date GLOB '??/??/????'),
            payment_method TEXT    NOT NULL CHECK(payment_method IN ('Cartão','Pix')),
            entry_type     TEXT    NOT NULL CHECK(entry_type IN ('Receita','Despesa')),
            value          REAL    NOT NULL CHECK(value > 0),
            account_id     INTEGER NOT NULL REFERENCES accounts(id),
            category       TEXT    NOT NULL,
            notes          TEXT    NOT NULL DEFAULT ''
        )
    """)
 
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mov_data    ON movements (date DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mov_account ON movements (account_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_mov_type    ON movements (entry_type)")
 
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_mov_account_entry_type
        ON movements (account_id, entry_type)
    """)
 
    _seed(conn, "accounts", [
        "Inter", "Itaú", "Caixa", "Porto", "MagaluPay", "Ticket",
    ])
    _seed(conn, "categories", [
        "Outros", "Carro", "Academia", "Pagamentos", "Curso", "Estética",
        "Lazer", "Mercado", "Farmacia", "Presentes", "Vestuario", "Viagem",
        "Celular", "Refeição", "Uber",
    ])
 
    conn.commit()


# ══════════════════════════════════════════════════════════════════════════════
# contas
# ══════════════════════════════════════════════════════════════════════════════
def list_accounts() -> list[dict]:
    rows = _db.conn.execute("SELECT id, name FROM accounts ORDER BY name").fetchall()
    return _rows_to_dicts(rows)
 
 
def insert_account(name: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError("O nome da conta não pode ser vazio.")
    try:
        cursor = _db.conn.execute("INSERT INTO accounts (name) VALUES (?)", (name,))
        _db.conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Conta '{name}' já existe.")
 
 
def get_account_summary(account_id: int) -> dict:
    row = _db.conn.execute("""
        SELECT
            COUNT(*)                                                AS count,
            COALESCE(SUM(CASE WHEN entry_type='Receita' THEN value END), 0) AS receita,
            COALESCE(SUM(CASE WHEN entry_type='Despesa' THEN value END), 0) AS despesa,
            COALESCE(SUM(CASE WHEN entry_type='Receita' THEN value
                              WHEN entry_type='Despesa' THEN -value END), 0) AS balance
        FROM movements
        WHERE account_id = ?
    """, (account_id,)).fetchone()
    return dict(row)


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIAS
# ══════════════════════════════════════════════════════════════════════════════
def list_categories() -> list[dict]:
    rows = _db.conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    return _rows_to_dicts(rows)
 
 
def insert_category(name: str) -> int:
    name = name.strip()
    if not name:
        raise ValueError("O nome da categoria não pode ser vazio.")
    try:
        cursor = _db.conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        _db.conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Categoria '{name}' já existe.")


# ══════════════════════════════════════════════════════════════════════════════
# MOVIMENTAÇÕES
# ══════════════════════════════════════════════════════════════════════════════
def list_movements() -> list[dict]:
    rows = _db.conn.execute("""
        SELECT
            m.id,
            m.date,
            m.payment_method,
            m.entry_type,
            m.value,
            m.account_id,
            a.name  AS account,
            m.category,
            m.notes
        FROM movements m
        JOIN accounts a ON a.id = m.account_id
        ORDER BY m.date DESC
    """).fetchall()
    return _rows_to_dicts(rows)


def insert_movement(
    date: str,
    payment_method: str,
    entry_type: str,
    value: float,
    account_id: int,
    category: str,
    notes: str = '',
) -> int:
    _validate_movement(entry_type, value)
    cursor = _db.conn.execute(
        """
        INSERT INTO movements
            (date, payment_method, entry_type, value, account_id, category, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (date, payment_method, entry_type, value, account_id, category, notes),
    )
    _db.conn.commit()
    return cursor.lastrowid


def delete_movement(mov_id: int) -> None:
    _db.conn.execute("DELETE FROM movements WHERE id = ?", (mov_id,))
    _db.conn.commit()


def search_movement(mov_id: int) -> dict | None:
    row = _db.conn.execute("SELECT * FROM movements WHERE id = ?", (mov_id,)).fetchone()
    return dict(row) if row else None


def update_movement(
    mov_id: int,
    date: str,
    payment_method: str,
    entry_type: str,
    value: float,
    account_id: int,
    category: str,
    notes: str = '',
) -> None:
    _validate_movement(entry_type, value)
    _db.conn.execute(
        """
        UPDATE movements
        SET date           = ?,
            payment_method = ?,
            entry_type     = ?,
            value          = ?,
            account_id     = ?,
            category       = ?,
            notes          = ?
        WHERE id = ?
        """,
        (date, payment_method, entry_type, value, account_id, category, notes, mov_id),
    )
    _db.conn.commit()


def _validate_movement(entry_type: str, value: float) -> None:
    if entry_type not in ("Receita", "Despesa"):
        raise ValueError(f"Tipo inválido: {entry_type!r}")
    if value <= 0:
        raise ValueError("Valor deve ser maior que zero.")


def close_database() -> None:
    _db.close()
