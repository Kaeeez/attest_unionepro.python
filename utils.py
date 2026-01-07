from decimal import Decimal, InvalidOperation

def parse_combo_id(value: str) -> int | None:
    if not value or ':' not in value:
        return None
    left = value.split(':', 1)[0].strip()
    try:
        return int(left)
    except ValueError:
        return None

def to_decimal_safe(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return Decimal('0')