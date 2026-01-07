import os
from typing import Sequence
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from models import Employee, Task, Project, DONE_STATUS

_conn = None

def init_db():
    global _conn
    if _conn:
        return _conn

    _conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'postgres'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'Lp9374621'),
        port=int(os.getenv('DB_PORT', '5432')),
        )
    return _conn

def close_db():
    global _conn
    if _conn:
        _conn.close()
        _conn = None

def execute_sql(query: str, params: Sequence | None = None):
    conn = init_db()
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()

def fetchall_sql(query: str, params: Sequence | None = None):
    conn = init_db()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, params)
        return cur.fetchall()

def get_employees() -> list[Employee]:
    rows = fetchall_sql('SELECT id, name, position, salary, COALESCE(hours_worked, 0) AS hours_worked FROM employees ORDER BY id')
    result = []
    for r in rows:
        result.append(
            Employee(
                id=r['id'],
                name=r['name'],
                position=r['position'],
                salary=Decimal(str(r['salary'])),
                hours_worked=Decimal(str(r['hours_worked'])),
                )
            )
        return result

def add_employee(name: str, position: str, salary):
    execute_sql('INSERT INTO employees (name, position, salary, hours_worked) VALUES (%s, %s, %s, %s)', (name, position, salary, 0))

def add_employee_hours(emp_id: int, hours: float):
    execute_sql('UPDATE employees SET hours_worked = COALESCE(hours_worked,0) + %s WHERE id = %s', (hours, emp_id))

def get_projects() -> list[Project]:
    rows = fetchall_sql('SELECT id, name FROM projects ORDER BY id')
    return [Project(id=r['id'], name=r['name']) for r in rows]
def add_project(name: str):
    execute_sql('INSERT INTO projects (name) VALUES (%s)', (name,))

def get_tasks() -> list[Task]:
    rows = fetchall_sql('SELECT id, title, description, status, project_id, employee_id FROM tasks ORDER BY id')
    return [
        Task(
            id=r['id'],
            title=r['title'],
            description=r['description'],
            status=r['status'],
            project_id=r['project_id'],
            employee_id=r['employee_id'],
            )
    for r in rows
        ]

def add_task(title: str, description: str, status: str = 'В процессе'):
    execute_sql('INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)', (title, description, status))

def set_task_project(task_id: int, project_id: int | None):
    execute_sql('UPDATE tasks SET project_id = %s WHERE id = %s', (project_id, task_id))

def set_task_employee(task_id: int, employee_id: int | None):
    execute_sql('UPDATE tasks SET employee_id = %s WHERE id = %s', (employee_id, task_id))

def update_task_status(task_id: int, status: str):
    execute_sql('UPDATE tasks SET status = %s WHERE id = %s', (status, task_id))

def get_project_counts(project_id: int) -> tuple[int, int]:
    total = fetchall_sql('SELECT COUNT(*) AS c FROM tasks WHERE project_id = %s', (project_id,))
    done = fetchall_sql('SELECT COUNT(*) AS c FROM tasks WHERE project_id = %s AND status = %s', (project_id, DONE_STATUS))
    total_count = total[0]['c'] if total else 0
    done_count = done[0]['c'] if done else 0
    return total_count, done_count

def get_employee_hours_salary(emp_id: int) -> tuple[Decimal, Decimal]:
    rows = fetchall_sql('SELECT COALESCE(hours_worked,0) AS hours_worked, COALESCE(salary,0) AS salary FROM employees WHERE id = %s', (emp_id,))
    if not rows:
        raise ValueError('Сотрудник не найден')
    r = rows[0]
    return Decimal(str(r['hours_worked'])), Decimal(str(r['salary']))

def bulk_insert_from_csv(file_path: str, table_name: str, columns: list[str]) -> int:
    df = pd.read_csv(file_path).dropna(how='all')
    if df.empty:
        return 0
    conn = init_db()
    inserted = 0
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            values = [row[col] for col in columns]
        placeholders = ','.join(['%s'] * len(values))
    sql = f'INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})'
    cur.execute(sql, values)
    inserted += 1
    conn.commit()
    return inserted