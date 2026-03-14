import csv
import sqlite3
from pathlib import Path

from database import (
    DB_PATH,
    insert_account,
    insert_movement,
    list_accounts,
    list_movements,
)

BASE_DIR = Path(__file__).parent
BACKUP_PATH = BASE_DIR / 'financas_backup.csv'

HEADER = [
    'id',
    'data',
    'modo_pagamento',
    'tipo',
    'valor',
    'conta',
    'categoria',
    'observacao',
]


def export_csv(path: str | Path = BACKUP_PATH) -> Path:
    path = Path(path)
    movs = list_movements()

    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=HEADER, delimiter=';')
        writer.writeheader()
        for m in movs:
            writer.writerow({k: m.get(k, '') for k in HEADER})

    return path


def import_csv(
    path: str | Path = BACKUP_PATH, overwrite: bool = False
) -> tuple[int, list[str]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {path}')

    erros: list[str] = []
    imported: int = 0

    if overwrite:
        _clear_database()

    account_cache: dict[str, int] = {c['name']: c['id'] for c in list_accounts()}

    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')

        required_fields = {
            'data',
            'modo_pagamento',
            'tipo',
            'valor',
            'conta',
            'categoria',
        }
        if not required_fields.issubset(set(reader.fieldnames or [])):
            raise ValueError(
                f'CSV inválido. Colunas esperadas: {required_fields}. '
                f'Encontradas: {reader.fieldnames}'
            )

        for i, line in enumerate(reader, start=2):
            try:
                value = float(str(line['valor']).replace(',', '.'))
                account_name = line['conta'].strip()

                if account_name not in account_cache:
                    new_id = insert_account(account_name)
                    account_cache[account_name] = new_id

                insert_movement(
                    data=line['data'].strip(),
                    payment_method=line['modo_pagamento'].strip(),
                    tipo=line['tipo'].strip(),
                    value=value,
                    cartao_id=account_cache[account_name],
                    categoria=line['categoria'].strip(),
                    observacao=line.get('observacao', '').strip(),
                )
                imported += 1
            except Exception as exc:
                erros.append(f'Linha {i}: {exc}')

    return imported, erros


def _clear_database() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('DELETE FROM movements')
        conn.execute("DELETE FROM sqlite_sequence WHERE name='movements'")
        conn.commit()


def default_backup_path() -> Path:
    return BACKUP_PATH
