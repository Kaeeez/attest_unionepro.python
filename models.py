from dataclasses import dataclass, field
from decimal import Decimal

IN_PROGRESS = 'В процессе'
DONE_STATUS = 'Завершена'

@dataclass
class Employee:
    id: int
    name: str
    position: str
    salary: Decimal
    hours_worked: Decimal = Decimal('0')

    def add_hours(self, hours: Decimal):
        if hours < 0:
            raise ValueError('Количество часов не может быть отрицательным')
        self.hours_worked += hours

@dataclass
class Task:
    id: int
    title: str
    description: str
    status: str
    project_id: int | None = None
    employee_id: int | None = None

    def str(self):
        status_icon = '✓' if self.status == DONE_STATUS else '◷'
        return f"{status_icon} {self.title}"

@dataclass
class Project:
    id: int
    name: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise TypeError('Должен быть передан объект Task')
        self.tasks.append(task)