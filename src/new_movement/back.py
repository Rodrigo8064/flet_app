from dataclasses import dataclass, field
from datetime import datetime

import database as db


_PAYMENT_METHODS = ["Cartão", "Pix"]

@dataclass
class FormData:
    accounts: list[dict]
    categories: list[dict]
    payment_methods: list[str]
    account_map: dict[str, int]


@dataclass
class NewMovementState:
    selected_entry_type: str = "Despesa"
    today: str = field(default_factory=lambda: datetime.today().strftime("%d/%m/%Y"))


def load_form_data() -> FormData:
    accounts = db.list_accounts()
    categories = db.list_categories()
    account_map = {a["name"]: a["id"] for a in accounts}

    return FormData(
        accounts=accounts,
        categories=categories,
        payment_methods=_PAYMENT_METHODS,
        account_map=account_map,
    )


def save_movement(
    date: str,
    payment_method: str,
    entry_type: str,
    raw_value: str,
    account_name: str,
    category: str,
    notes: str,
    account_map: dict[str, int],
) -> str | None:
    if not date:
        return "Preencha a data."
    if not raw_value:
        return "Preencha o valor."
    if not payment_method:
        return "Preencha o método de pagamento."
    if not account_name:
        return "Selecione a conta."
    if not category:
        return "Selecione a categoria."

    try:
        value = float(raw_value.replace(".", "").replace(",", "."))
        if value <= 0:
            raise ValueError
    except ValueError:
        return "Valor inválido."

    account_id = account_map.get(account_name)
    if account_id is None:
        return "Conta inválida."

    try:
        db.insert_movement(
            date=date,
            payment_method=payment_method,
            entry_type=entry_type,
            value=value,
            account_id=account_id,
            category=category,
            notes=notes,
        )
    except Exception as error:
        return f"Erro ao salvar: {error}"

    return None


def save_category(name: str) -> str | None:
    try:
        db.insert_category(name or "")
        return None
    except ValueError as error:
        return str(error)
