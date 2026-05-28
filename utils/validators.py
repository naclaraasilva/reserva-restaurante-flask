import re
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))


def parse_date(value: str) -> datetime:
    ##converte string para date
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except (ValueError, TypeError):
        raise ValueError(
            f"Formato de data inválido. Use: '{DATE_FORMAT}' (ex: '2026-04-20')"
        )


def parse_time(value: str) -> str:
    ##valida formato de hora HH:MM
    try:
        datetime.strptime(value, TIME_FORMAT)
        return value
    except (ValueError, TypeError):
        raise ValueError(
            f"Formato de hora inválido. Use: '{TIME_FORMAT}' (ex: '19:30')"
        )


def validate_required_fields(data: dict, fields: list) -> list:
    #retorna lista de campos obrigatorios ausentes ou vazios
    return [f for f in fields if data.get(f) is None or data.get(f) == ""]
