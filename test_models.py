import unittest
from decimal import Decimal
from models import Employee, Task, Project, IN_PROGRESS, DONE_STATUS

class TestEmployee(unittest.TestCase):
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

class TestTask(unittest.TestCase):
    def test_str_done(self):
        task = Task(id=1, title='Выполнить задачу', description='Тестовая задача', status=DONE_STATUS)
        expected = "✓ Выполнить задачу"
        self.assertEqual(task.str(), expected)

    def test_str_in_progress(self):
        task = Task(id=2, title='Сделать отчет', description='Тест2', status=IN_PROGRESS)
        expected = "◷ Сделать отчет"
        self.assertEqual(task.str(), expected)

    def test_project_employee_id(self):
        task = Task(id=3, title='Вторая', description='...', status=IN_PROGRESS, project_id=10, employee_id=20)
        self.assertEqual(task.project_id, 10)
        self.assertEqual(task.employee_id, 20)

class TestProject(unittest.TestCase):
    def test_add_task(self):
        proj = Project(id=1, name='Проект 1')
        task = Task(id=1, title='Задача 1', description='Тест', status=IN_PROGRESS)
        proj.add_task(task)
        self.assertEqual(len(proj.tasks), 1)
        self.assertIs(proj.tasks[0], task)

    def test_add_task_type_error(self):
        proj = Project(id=2, name='Проект 2')
        with self.assertRaises(TypeError):
            proj.add_task('Не задача')


if __name__ == '__main__':
    unittest.main()
