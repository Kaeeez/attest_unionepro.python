from decimal import Decimal, InvalidOperation

def calculate_pay(hours, salary, base_hours=Decimal('160'), overtime_rate=Decimal('1.5')) -> Decimal:
    try:
        hours = Decimal(str(hours if hours is not None else 0))
        salary = Decimal(str(salary if salary is not None else 0))
    except (InvalidOperation, TypeError):
        raise ValueError('Некорректные hours/salary для расчета')
    hourly_rate = salary / base_hours if base_hours != 0 else Decimal('0')
    regular_hours = hours if hours <= base_hours else base_hours
    overtime_hours = hours - base_hours if hours > base_hours else Decimal('0')
    pay = (regular_hours * hourly_rate) + (overtime_hours * hourly_rate * overtime_rate)
    return pay.quantize(Decimal('0.01'))

def project_progress(done_count: int, total_count: int) -> float:
    if not total_count:
        return 0.0
    return done_count / total_count * 100.0