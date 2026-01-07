import tkinter as tk
# from logging import root
from tkinter import ttk, messagebox, filedialog
from decimal import Decimal
from models import IN_PROGRESS, DONE_STATUS
import storage
import analysis
from utils import parse_combo_id

### Локальное состояние (кэши) для комбобоксов/таблиц

employees_cache = []
projects_cache = []
tasks_cache = []

def run_app():
    storage.init_db()
    root = tk.Tk()
    root.title('Учёт, задачи, проекты + импорт CSV')
    root.geometry('1200x700')

    tab_control = ttk.Notebook(root)

    tab_main = ttk.Frame(tab_control)
    tab_employees = ttk.Frame(tab_control)
    tab_tasks = ttk.Frame(tab_control)
    tab_projects = ttk.Frame(tab_control)
    tab_actions = ttk.Frame(tab_control)

    tab_control.add(tab_main, text='Главное')
    tab_control.add(tab_employees, text='Сотрудники')
    tab_control.add(tab_projects, text='Проекты')
    tab_control.add(tab_tasks, text='Задачи')
    tab_control.add(tab_actions, text='Расчёт')
    tab_control.pack(expand=1, fill='both')

    ### -- Главная --

    ttk.Label(tab_main, text='Добро пожаловать! Используйте вкладки.', font=('Arial', 14)).pack(pady=20)

    ### -- Сотрудники --

    ttk.Label(tab_employees, text='ФИО:', anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    entry_emp_name = ttk.Entry(tab_employees, width=60)
    entry_emp_name.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(tab_employees, text='Должность:', anchor='w').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    entry_emp_pos = ttk.Entry(tab_employees, width=60)
    entry_emp_pos.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(tab_employees, text='Зарплата:', anchor='w').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    entry_emp_salary = ttk.Entry(tab_employees, width=60)
    entry_emp_salary.grid(row=2, column=1, padx=5, pady=5)
    columns_emp = ("id", "name", "position", "salary")
    tree_employees = ttk.Treeview(tab_employees, columns=columns_emp, show='headings')

    for c in columns_emp:
        tree_employees.heading(c, text=c)
        tree_employees.column('id', width=60, anchor='center')
        tree_employees.column('name', width=180, anchor='w')
        tree_employees.column('position', width=180, anchor='w')
        tree_employees.column('salary', width=100, anchor='e')
        tree_employees.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

    def clear_emp_fields():
        entry_emp_name.delete(0, tk.END)
        entry_emp_pos.delete(0, tk.END)
        entry_emp_salary.delete(0, tk.END)

    def refresh_employees():
        employees_cache.clear()
        employees_cache.extend(storage.get_employees())
        refresh_employees_table()

    def refresh_employees_table():
        for row in tree_employees.get_children():
            tree_employees.delete(row)
        for e in employees_cache:
            tree_employees.insert("", "end", values=(e.id, e.name, e.position, str(e.salary)))

    def add_employee():
        name = entry_emp_name.get().strip()
        pos = entry_emp_pos.get().strip()
        try:
            salary = float(entry_emp_salary.get())
        except Exception:
            messagebox.showerror("Ошибка", "Введите числовое значение зарплаты")
            return
        if not name:
            messagebox.showwarning("Внимание", "Введите имя")
            return
        try:
            storage.add_employee(name, pos, salary)
            refresh_employees()
            clear_emp_fields()
        except Exception as e:
            messagebox.showerror("Ошибка базы", str(e))

    def import_employees_csv():
        filename = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv")])
        if not filename:
            return
        try:
            inserted = storage.bulk_insert_from_csv(filename, "employees", ["name", "position", "salary"])
            messagebox.showinfo("Импорт", f"Загружено строк: {inserted}")
            refresh_employees()
            refresh_all_combos()
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

    ttk.Button(tab_employees, text="Добавить сотрудника", command=add_employee).grid(row=3, column=0, padx=5, pady=5)
    ttk.Button(tab_employees, text="Загрузить CSV", command=import_employees_csv).grid(row=3, column=1, padx=5, pady=5)

    ### -- Проекты --

    ttk.Label(tab_projects, text="Название проекта:", anchor='w').grid(row=0, column=0, padx=5, pady=5)
    entry_proj_name = ttk.Entry(tab_projects, width=60)
    entry_proj_name.grid(row=0, column=1, padx=5, pady=5)
    columns_projects = ("id", "name")
    tree_projects = ttk.Treeview(tab_projects, columns=columns_projects, show='headings')

    for c in columns_projects:
        tree_projects.heading(c, text=c)
        tree_projects.column('id', width=60, anchor='center')
        tree_projects.column('name', width=260, anchor='w')
        tree_projects.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

    def refresh_projects():
        projects_cache.clear()
        projects_cache.extend(storage.get_projects())
        for row in tree_projects.get_children():
            tree_projects.delete(row)
        for p in projects_cache:
            tree_projects.insert("", "end", values=(p.id, p.name))

    def create_project():
        name = entry_proj_name.get().strip()
        if not name:
            messagebox.showwarning("Внимание", "Введите имя проекта")
            return
        try:
            storage.add_project(name)
            entry_proj_name.delete(0, tk.END)
            refresh_projects()
            refresh_all_combos()
        except Exception as e:
            messagebox.showerror("Ошибка базы", str(e))

    def import_projects_csv():
        filename = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv")])
        if not filename:
            return
        try:
            inserted = storage.bulk_insert_from_csv(filename, "projects", ["name"])
            messagebox.showinfo("Импорт", f"Загружено строк: {inserted}")
            refresh_projects()
            refresh_all_combos()
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

    ttk.Button(tab_projects, text="Создать проект", command=create_project).grid(row=1, column=0, padx=5, pady=5)
    ttk.Button(tab_projects, text="Загрузить CSV", command=import_projects_csv).grid(row=1, column=1, padx=5, pady=5)

    ### -- Задачи --

    ttk.Label(tab_tasks, text="Название:", anchor='w').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    entry_task_title = ttk.Entry(tab_tasks, width=60)
    entry_task_title.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(tab_tasks, text="Описание:", anchor='w').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    entry_task_desc = ttk.Entry(tab_tasks, width=60)
    entry_task_desc.grid(row=1, column=1, padx=5, pady=5)

    columns_tasks = ("id", "title", "description", "status")
    tree_tasks = ttk.Treeview(tab_tasks, columns=columns_tasks, show='headings')
    for c in columns_tasks:
        tree_tasks.heading(c, text=c)
        tree_tasks.column('id', width=60, anchor='center')
        tree_tasks.column('title', width=260, anchor='w')
        tree_tasks.column('description', width=320, anchor='w')
        tree_tasks.column('status', width=100, anchor='center')
        tree_tasks.grid(row=4, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

    def refresh_tasks():
        tasks_cache.clear()
        tasks_cache.extend(storage.get_tasks())
        for row in tree_tasks.get_children():
            tree_tasks.delete(row)
        for t in tasks_cache:
            tree_tasks.insert("", "end", values=(t.id, t.title, t.description, t.status))

    def add_task():
        title = entry_task_title.get().strip()
        desc = entry_task_desc.get().strip()
        if not title:
            messagebox.showwarning("Внимание", "Введите название задачи")
            return
        storage.add_task(title, desc, IN_PROGRESS)
        refresh_tasks()
        refresh_all_combos()
        entry_task_title.delete(0, tk.END)
        entry_task_desc.delete(0, tk.END)

    def import_tasks_csv():
        filename = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv")])
        if not filename:
            return
        try:
            inserted = storage.bulk_insert_from_csv(filename, "tasks", ["title", "description", "status"])
            messagebox.showinfo("Импорт", f"Загружено строк: {inserted}")
            refresh_tasks()
            refresh_all_combos()
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))

    ttk.Button(tab_tasks, text="Добавить задачу", command=add_task).grid(row=3, column=0, padx=5, pady=5)
    ttk.Button(tab_tasks, text="Загрузить CSV", command=import_tasks_csv).grid(row=3, column=1, padx=5, pady=5)

    ### -- Расчет --
    ### -- Действия --

    ttk.Label(tab_actions, text="Добавить задачу в проект").grid(row=0, column=0, padx=5, pady=10, sticky='w')
    ttk.Label(tab_actions, text="Выберите проект:").grid(row=1, column=0, padx=5, pady=2, sticky='w')

    combo_project_add_task = ttk.Combobox(tab_actions, state='readonly')
    combo_project_add_task.grid(row=3, column=0, padx=5, pady=2, sticky='w')

    ttk.Label(tab_actions, text="Выберите задачу:").grid(row=4, column=0, padx=5, pady=2, sticky='w')
    combo_task_add_project = ttk.Combobox(tab_actions, state='readonly')
    combo_task_add_project.grid(row=6, column=0, padx=5, pady=2, sticky='w')

    def populate_projects_combo():
        refresh_projects()
        combo_project_add_task['values'] = [f"{p.id}: {p.name}" for p in projects_cache]

    def populate_tasks_combo():
        refresh_tasks()
        combo_task_add_project['values'] = [f"{t.id}: {t.title}" for t in tasks_cache]

    ttk.Button(tab_actions, text="Обновить список проектов", command=populate_projects_combo).grid(row=2, column=0, padx=5, pady=5, sticky='w')
    ttk.Button(tab_actions, text="Обновить список задач", command=populate_tasks_combo).grid(row=5, column=0, padx=5, pady=5, sticky='w')

    def add_task_in_project():
        p_id = parse_combo_id(combo_project_add_task.get())
        t_id = parse_combo_id(combo_task_add_project.get())
        if not p_id or not t_id:
            messagebox.showwarning("Внимание", "Выберите проект и задачу")
            return
        try:
            storage.set_task_project(task_id=t_id, project_id=p_id)
            messagebox.showinfo("Успех", "Задача привязана к проекту")
            populate_tasks_combo()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    ttk.Button(tab_actions, text="Добавить задачу в проект", command=add_task_in_project).grid(row=7, column=0, padx=5, pady=5, sticky='w')

    ### -- Назначение задачи сотруднику --

    ttk.Label(tab_actions, text="Назначить задачу сотруднику").grid(row=0, column=1, padx=5, pady=10, sticky='w')
    ttk.Label(tab_actions, text="Выберите сотрудника:").grid(row=1, column=1, padx=5, pady=2, sticky='w')

    combo_emp_assign = ttk.Combobox(tab_actions, state='readonly')
    combo_emp_assign.grid(row=3, column=1, padx=5, pady=2, sticky='w')
    combo_task_assign = ttk.Combobox(tab_actions, state='readonly')
    combo_task_assign.grid(row=6, column=1, padx=5, pady=2, sticky='w')

    def refresh_emp_assign():
        refresh_employees()
        combo_emp_assign['values'] = [f"{e.id}: {e.name}" for e in employees_cache]

    def refresh_task_assign():
        refresh_tasks()
        combo_task_assign['values'] = [f"{t.id}: {t.title}" for t in tasks_cache]

    ttk.Button(tab_actions, text="Обновить список сотрудников", command=refresh_emp_assign).grid(row=2, column=1, padx=5, pady=5, sticky='w')
    ttk.Button(tab_actions, text="Обновить список задач", command=refresh_task_assign).grid(row=5, column=1, padx=5, pady=5, sticky='w')

    def assign_task():
        t_id = parse_combo_id(combo_task_assign.get())
        e_id = parse_combo_id(combo_emp_assign.get())
        if not t_id or not e_id:
            messagebox.showwarning("Внимание", "Выберите задачу и сотрудника")
            return
        storage.set_task_employee(t_id, e_id)
        messagebox.showinfo("Успех", "Задача назначена")
        refresh_tasks()

    ttk.Button(tab_actions, text="Назначить задачу", command=assign_task).grid(row=7, column=1, padx=5, pady=5, sticky='w')

    ### -- Добавление часов сотруднику --

    ttk.Label(tab_actions, text="Добавить часы сотруднику").grid(row=0, column=2, padx=5, pady=5, sticky='w')
    ttk.Label(tab_actions, text="Выберите сотрудника:").grid(row=1, column=2, padx=5, pady=2, sticky='w')
    combo_emp_hours = ttk.Combobox(tab_actions, state='readonly')
    combo_emp_hours.grid(row=3, column=2, padx=5, pady=2, sticky='w')

    ttk.Label(tab_actions, text="Часов:").grid(row=4, column=2, padx=5, pady=2, sticky='w')
    entry_hours = ttk.Entry(tab_actions, width=10)
    entry_hours.grid(row=5, column=2, padx=5, pady=2, sticky='w')

    def refresh_employees_combo():
        refresh_employees()
        combo_emp_hours['values'] = [f"{e.id}: {e.name}" for e in employees_cache]

    def add_hours():
        emp_id = parse_combo_id(combo_emp_hours.get())
        if not emp_id:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return
        try:
            hours = float(entry_hours.get())
        except Exception:
            messagebox.showerror("Ошибка", "Введите число часов")
            return
        storage.add_employee_hours(emp_id, hours)
        messagebox.showinfo("Успех", "Часы добавлены")
        refresh_employees()

    ttk.Button(tab_actions, text="Обновить список сотрудников", command=refresh_employees_combo).grid(row=2, column=2, padx=5, pady=5)
    ttk.Button(tab_actions, text="Добавить часы", command=add_hours).grid(row=6, column=2, padx=5, pady=5, sticky='w')

    ### -- Обновить статус задачи --

    ttk.Label(tab_actions, text="Обновить статус задачи").grid(row=0, column=3, padx=5, pady=10, sticky='w')
    ttk.Label(tab_actions, text="Название задачи:").grid(row=1, column=3, padx=5, pady=2, sticky='w')
    combo_task_status = ttk.Combobox(tab_actions, state='readonly')
    combo_task_status.grid(row=3, column=3, padx=5, pady=2, sticky='w')

    ttk.Label(tab_actions, text="Статус:").grid(row=4, column=3, padx=5, pady=2, sticky='w')
    combo_status = ttk.Combobox(tab_actions, values=[IN_PROGRESS, DONE_STATUS], state='readonly')
    combo_status.grid(row=5, column=3, padx=5, pady=2, sticky='w')

    def refresh_task_for_status():
        refresh_tasks()
        combo_task_status['values'] = [f"{t.id}: {t.title}" for t in tasks_cache]

    def update_task_status():
        t_id = parse_combo_id(combo_task_status.get())
        s = combo_status.get().strip()
        if not t_id or not s:
            messagebox.showwarning("Внимание", "Выберите задачу и статус")
            return
        if s not in (IN_PROGRESS, DONE_STATUS):
            messagebox.showerror("Ошибка", f"Недопустимый статус: {s}")
            return
        storage.update_task_status(t_id, s)
        messagebox.showinfo("Готово", "Статус задачи обновлён")
        refresh_task_for_status()

    ttk.Button(tab_actions, text="Обновить список задач", command=refresh_task_for_status).grid(row=2, column=3, padx=5, pady=5, sticky='w')
    ttk.Button(tab_actions, text="Обновить статус", command=update_task_status).grid(row=6, column=3, padx=5, pady=5, sticky='w')

    ### -- Прогресс проекта --

    ttk.Label(tab_actions, text="Прогресс проекта").grid(row=0, column=4, padx=5, pady=10, sticky='w')
    ttk.Label(tab_actions, text="Выберите проект:").grid(row=1, column=4, padx=5, pady=2, sticky='w')
    combo_project_progress = ttk.Combobox(tab_actions, state='readonly')
    combo_project_progress.grid(row=3, column=4, padx=5, pady=2, sticky='w')

    def populate_projects_combo_progress():
        refresh_projects()
        combo_project_progress['values'] = [f"{p.id}: {p.name}" for p in projects_cache]

    def show_progress():
        p_id = parse_combo_id(combo_project_progress.get())
        if not p_id:
            messagebox.showwarning("Внимание", "Выберите проект")
            return
        total, done = storage.get_project_counts(p_id)
        prog = analysis.project_progress(done, total)
        messagebox.showinfo("Прогресс проекта", f"Прогресс: {prog:.2f}% ({done}/{total})")

    ttk.Button(tab_actions, text="Обновить список проектов", command=populate_projects_combo_progress).grid(row=2, column=4, padx=5, pady=5, sticky='w')
    ttk.Button(tab_actions, text="Показать прогресс проекта", command=show_progress).grid(row=4, column=4, padx=5, pady=5)

    ### -- Расчет зарплаты --

    ttk.Label(tab_actions, text="Расчет зарплаты сотруднику").grid(row=0, column=6, padx=5, pady=5, sticky='w')
    ttk.Label(tab_actions, text="Выберите сотрудника:").grid(row=1, column=6, padx=5, pady=2, sticky='w')
    combo_emp_pay = ttk.Combobox(tab_actions, state='readonly')
    combo_emp_pay.grid(row=3, column=6, padx=5, pady=2, sticky='w')

    def refresh_employees_pay():
        refresh_employees()
        combo_emp_pay['values'] = [f"{e.id}: {e.name}" for e in employees_cache]

    def calc_salary():
        emp_id = parse_combo_id(combo_emp_pay.get())
        if not emp_id:
            messagebox.showwarning("Внимание", "Выберите сотрудника")
            return
        try:
            hours, salary = storage.get_employee_hours_salary(emp_id)
            pay = analysis.calculate_pay(hours, salary, base_hours=Decimal("160"), overtime_rate=Decimal("1.5"))
            messagebox.showinfo("Заработок", f"Заработано: {pay}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    ttk.Button(tab_actions, text="Обновить список сотрудников", command=refresh_employees_pay).grid(row=2, column=6, padx=5, pady=5)
    ttk.Button(tab_actions, text="Рассчитать зарплату", command=calc_salary).grid(row=4, column=6, padx=5, pady=5, sticky='w')

### -- Общие обновления --

    def refresh_all_combos():
        refresh_employees_pay()
        refresh_employees_combo()
        refresh_emp_assign()
        refresh_task_assign()
        populate_projects_combo()
        populate_tasks_combo()
        populate_projects_combo_progress()

    ### -- Первый запуск — загрузка таблиц и комбо --

    refresh_employees()
    refresh_projects()
    refresh_tasks()
    refresh_all_combos()

    def on_close():
        storage.close_db()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()