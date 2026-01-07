import unittest
from decimal import Decimal
from models import Employee, Task, Project, IN_PROGRESS, DONE_STATUS

c(unittest.TestCase):
    def test_add_hours_positive(self):
        emp = Employee(id=1, name='Иван', position='разработчик', salary=Decimal('100000'))
        emp.add_hours(Decimal('8'))
        self.assertEqual(emp.hours_worked, Decimal('8'))
        emp.add_hours(Decimal('2.5'))
        self.assertEqual(emp.hours_worked, Decimal('10.5'))

    def test_add_hours_negative(self):
        emp = Employee(id=2, name='Мария', position='тестировщик', salary=Decimal('90000'))
        with self.assertRaises(ValueError):
            emp.add_hours(Decimal('-5'))