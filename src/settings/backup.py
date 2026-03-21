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


class ExportCSV:
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

    FIELD_MAPPING: dict[str, str] = {
        'id': 'id',
        'data': 'date',
        'modo_pagamento': 'payment_method',
        'tipo': 'entry_type',
        'valor': 'value',
        'conta': 'account',
        'categoria': 'category',
        'observacao': 'notes',
    }

    @classmethod
    def export(cls, path: str | Path = BACKUP_PATH) -> Path:
        path = Path(path)
        movements = list_movements()

        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=cls.HEADER, delimiter=',')
            writer.writeheader()

            for movement in movements:
                row = {
                    col: movement.get(cls.FIELD_MAPPING[col], "")
                    for col in cls.HEADER
                }
                writer.writerow(row)

        return path


class ImportCSV:
    REQUIRED_FIELDS = {
        'data',
        'modo_pagamento',
        'tipo',
        'valor',
        'conta',
        'categoria',
    }

    DEFAULT_PATH: Path = BACKUP_PATH

    @classmethod
    def import_all(
        cls,
        path: str | Path = BACKUP_PATH,
        overwrite: bool = False
    ) -> tuple[int, list[str]]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'Arquivo não encontrado: {path}')

        errors: list[str] = []
        imported: int = 0
        account_cache: dict[str, int] = {account['name']: account['id'] for account in list_accounts()}

        if overwrite:
            cls._clear_database()


        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=',')
            found_fields = set(reader.fieldnames or [])

            if not cls.REQUIRED_FIELDS.issubset(found_fields):
                raise ValueError(
                    f'CSV inválido. Colunas esperadas: {cls.REQUIRED_FIELDS}. '
                    f'Encontradas: {reader.fieldnames}'
                )

            for line_number, row in enumerate(reader, start=2):
                try:
                    value = float(row['valor'].replace(',', '.'))
                    account_name = row['conta'].strip()

                    if account_name not in account_cache:
                        account_cache[account_name] = insert_account(account_name)

                    insert_movement(
                        date=row['data'].strip(),
                        payment_method=row['modo_pagamento'].strip(),
                        entry_type=row['tipo'].strip(),
                        value=value,
                        account_id=account_cache[account_name],
                        category=row['categoria'].strip(),
                        notes=row.get('observacao', '').strip(),
                    )
                    imported += 1
                except Exception as error:
                    errors.append(f'Linha {line_number}: {error}')

        return imported, errors

    @classmethod
    def _clear_database(cls) -> None:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('DELETE FROM movements')
            conn.execute("DELETE FROM sqlite_sequence WHERE name='movements'")
            conn.commit()
