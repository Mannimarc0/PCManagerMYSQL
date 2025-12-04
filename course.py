import sys
import os
import logging
import platform
import subprocess
import mysql.connector
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog, QDialog, \
    QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QDateEdit
from ui_coursemanager import Ui_MainWindow
from validation import Validator, ValidationError, InvalidEmailError, DatabaseError
from PySide6.QtWidgets import QFileDialog
import pandas as pd
from report_generator import ReportGenerator
from report_dialog import ReportDialog

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="course_db",
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci"
    )
    cursor = conn.cursor()
    conn.commit()
    logger.info("Успешное подключение к базе данных")
except mysql.connector.Error as err:
    logger.critical(f"Ошибка подключения к базе данных: {err}")
    raise


class People:
    def __init__(self, id=None, name=None, contact=None):
        self._id = id
        self._name = None
        self._contact = None
        if name is not None:
            self.name = name
        if contact is not None:
            self.contact = contact

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            self._name = Validator.validate_non_empty(value, "Имя")
        else:
            self._name = value

    @property
    def contact(self):
        return self._contact

    @contact.setter
    def contact(self, value):
        if value is not None:
            self._contact = Validator.validate_email(value)
        else:
            self._contact = value


class Client(People):
    def __init__(self, id=None, name=None, contact=None):
        super().__init__(id=id, name=name, contact=contact)
        self._projects = []
        logger.debug(f"Создан объект Client: id={id}, name={name}, contact={contact}")

    @property
    def projects(self):
        return self._projects

    @projects.setter
    def projects(self, value):
        self._projects = value

    def save_to_db(self):
        try:
            sql = "INSERT INTO clients (client_name, client_contact) VALUES (%s, %s)"
            values = (self.name, self.contact)
            cursor.execute(sql, values)
            conn.commit()
            self.id = cursor.lastrowid
            logger.info(f"Клиент успешно добавлен в БД: ID={self.id}, Имя={self.name}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении клиента '{self.name}': {err}")
            return False


class Employee(People):
    def __init__(self, id=None, name=None, position=None, contact=None):
        # contact для сотрудника может быть опционален
        super().__init__(id=id, name=name, contact=contact)
        self._position = position
        self._tasks = []
        self._projects = []
        logger.debug(f"Создан объект Employee: id={id}, name={name}, position={position}")

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if value is not None:
            self._position = Validator.validate_non_empty(value, "Должность")
        else:
            self._position = value

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        self._tasks = value

    @property
    def projects(self):
        return self._projects

    @projects.setter
    def projects(self, value):
        self._projects = value

    def save_to_db(self):
        try:
            sql = "INSERT INTO employee (employee_name, employee_position) VALUES (%s, %s)"
            values = (self.name, self.position)
            cursor.execute(sql, values)
            conn.commit()
            self.id = cursor.lastrowid
            logger.info(f"Сотрудник успешно добавлен в БД: ID={self.id}, Имя={self.name}, Должность={self.position}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении сотрудника '{self.name}': {err}")
            return False


class Project:
    def __init__(self, id=None, name=None, client_id=None, start_date=None, end_date=None):
        self._id = id
        self._name = name
        self._client_id = client_id
        self._start_date = start_date
        self._end_date = end_date
        logger.debug(f"Создан объект Project: id={id}, name={name}, client_id={client_id}")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            self._name = Validator.validate_non_empty(value, "Название проекта")
        else:
            self._name = value

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def save_to_db(self):
        try:
            sql = """INSERT INTO project (project_name, project_client, project_start_date, project_end_date)
                     VALUES (%s, %s, %s, %s)"""
            values = (self.name, self.client_id, self.start_date, self.end_date)
            cursor.execute(sql, values)
            conn.commit()
            self.id = cursor.lastrowid
            logger.info(
                f"Проект успешно добавлен в БД: ID={self.id}, Название={self.name}, Период={self.start_date} - {self.end_date}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении проекта '{self.name}': {err}")
            return False


class Task:
    def __init__(self, id=None, description=None, project_id=None, due_date=None, status="in progress",
                 employee_id=None):
        self._id = id
        self._description = description
        self._project_id = project_id
        self._due_date = due_date
        self._status = status
        self._employee_id = employee_id
        logger.debug(
            f"Создан объект Task: id={id}, description={description}, project_id={project_id}, employee_id={employee_id}")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is not None:
            self._description = Validator.validate_non_empty(value, "Описание задачи")
        else:
            self._description = value

    @property
    def project_id(self):
        return self._project_id

    @project_id.setter
    def project_id(self, value):
        self._project_id = value

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        self._due_date = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        valid_statuses = ["in progress", "completed", "pending", "cancelled"]
        if value and value not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые: {', '.join(valid_statuses)}")
        self._status = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        self._employee_id = value

    def save_to_db(self):
        try:
            sql = """INSERT INTO task (task_description, task_project, task_due_date, task_status, \
                                       task_assigned_employee)
                     VALUES (%s, %s, %s, %s, %s)"""
            values = (self.description, self.project_id, self.due_date, self.status, self.employee_id)
            cursor.execute(sql, values)
            conn.commit()
            self.id = cursor.lastrowid
            logger.info(
                f"Задача успешно добавлена в БД: ID={self.id}, Описание={self.description}, Срок={self.due_date}")
            return True
        except mysql.connector.Error as err:
            logger.error(f"Ошибка при добавлении задачи '{self.description}': {err}")
            return False


class ProjectManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Инициализация приложения ProjectManagerApp")

        # Загружаем UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        logger.debug("UI успешно загружен")

        # Подключаем сигналы к слотам
        self.setup_connections()
        logger.debug("Сигналы подключены к слотам")

        # Устанавливаем минимальную дату для виджета задач (текущая дата)
        from PySide6.QtCore import QDate
        self.ui.date_task_due.setMinimumDate(QDate.currentDate())
        logger.debug("Установлена минимальная дата для срока выполнения задачи")

        # Загружаем данные
        self.load_all_data()
        logger.info("Приложение успешно инициализировано")

    def on_client_cell_click(self, row, column):
        # Обработка клика на ячейку клиента - показ информации при клике на ID
        if column == 0:  # Колонка ID
            try:
                client_id = self.ui.table_clients.item(row, 0).text()
                client_name = self.ui.table_clients.item(row, 1).text()
                client_contact = self.ui.table_clients.item(row, 2).text()

                # Подсчитываем количество проектов клиента
                cursor.execute(
                    "SELECT COUNT(*) FROM project WHERE project_client = %s",
                    (client_id,)
                )
                project_count = cursor.fetchone()[0]

                # Получаем список проектов
                cursor.execute(
                    "SELECT project_name FROM project WHERE project_client = %s",
                    (client_id,)
                )
                projects = cursor.fetchall()
                project_list = "\n  • " + "\n  • ".join([p[0] for p in projects]) if projects else "  Нет проектов"

                logger.info(
                    f"Просмотр информации о клиенте: ID={client_id}, Имя={client_name}, Проектов={project_count}")

                info_message = f"""
📋 Детальная информация о клиенте:

ID: {client_id}
Имя: {client_name}
Контакт: {client_contact}
Количество проектов: {project_count}

Проекты:
{project_list}
                """

                QMessageBox.information(
                    self,
                    "Информация о клиенте",
                    info_message
                )
            except Exception as e:
                logger.error(f"Не удалось загрузить информацию о клиенте: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить информацию: {e}")

    def on_client_double_click(self, row, column):
        logger.debug(f"Двойной клик по клиенту: строка={row}, колонка={column}")
        try:
            # Получаем данные из выбранной строки
            client_id = self.ui.table_clients.item(row, 0).text()
            client_name = self.ui.table_clients.item(row, 1).text()
            client_contact = self.ui.table_clients.item(row, 2).text()

            # Создаем диалог для редактирования
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать клиента #{client_id}")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout()

            # Поля ввода
            layout.addWidget(QLabel("Имя клиента:"))
            name_edit = QLineEdit(client_name)
            layout.addWidget(name_edit)

            layout.addWidget(QLabel("Контакт (Email):"))
            contact_edit = QLineEdit(client_contact)
            layout.addWidget(contact_edit)

            # Кнопки
            button_layout = QHBoxLayout()
            btn_save = QPushButton("Сохранить")
            btn_cancel = QPushButton("Отмена")
            button_layout.addWidget(btn_save)
            button_layout.addWidget(btn_cancel)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            # Обработчики кнопок
            def save_changes():
                try:
                    new_name = name_edit.text().strip()
                    new_contact = contact_edit.text().strip()

                    # Валидация
                    new_name, new_contact = Validator.validate_client_data(new_name, new_contact)

                    # Проверка уникальности email (исключая текущего клиента)
                    Validator.check_email_uniqueness(new_contact, cursor, exclude_id=client_id)

                    # Обновление в БД
                    cursor.execute(
                        "UPDATE clients SET client_name = %s, client_contact = %s WHERE client_id = %s",
                        (new_name, new_contact, client_id)
                    )
                    conn.commit()
                    logger.info(f"Клиент ID={client_id} успешно обновлен")

                    QMessageBox.information(dialog, "Успех", "Данные клиента обновлены!")
                    dialog.accept()
                    self.load_clients()

                except ValidationError as e:
                    QMessageBox.warning(dialog, "Ошибка валидации", str(e))
                except Exception as e:
                    logger.error(f"Ошибка обновления клиента: {e}")
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка обновления: {e}")

            btn_save.clicked.connect(save_changes)
            btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

        except Exception as e:
            logger.error(f"Не удалось открыть редактирование клиента: {e}")
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Не удалось открыть редактирование: {e}"
            )

    def on_project_date_changed(self, date):
        from PySide6.QtCore import QDate
        current_date = QDate.currentDate()
        start_date = self.ui.date_project_start.date()
        end_date = self.ui.date_project_end.date()

        logger.debug(
            f"Изменение дат проекта: начало={start_date.toString('yyyy-MM-dd')}, конец={end_date.toString('yyyy-MM-dd')}")

        if end_date < start_date:
            logger.warning(
                f"Некорректные даты проекта: дата окончания ({end_date.toString('yyyy-MM-dd')}) раньше даты начала ({start_date.toString('yyyy-MM-dd')})")
            QMessageBox.warning(
                self,
                "Ошибка валидации дат",
                f"Дата окончания ({end_date.toString('dd.MM.yyyy')}) "
                f"не может быть раньше даты начала ({start_date.toString('dd.MM.yyyy')})!\n\n"
                f"Дата окончания будет автоматически установлена на {start_date.toString('dd.MM.yyyy')}"
            )
            self.ui.date_project_end.setDate(start_date)
            logger.info(f"Дата окончания автоматически исправлена на {start_date.toString('yyyy-MM-dd')}")

    def closeEvent(self, event):
        logger.info("Запрос на закрытие приложения")
        # Запрашиваем подтверждение выхода
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",
            "Вы уверены, что хотите выйти из программы?\n\n"
            "Все несохраненные данные будут потеряны.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("Пользователь подтвердил выход из приложения")
            # Закрываем соединение с БД перед выходом
            try:
                cursor.close()
                conn.close()
                logger.info("Соединение с БД закрыто успешно")
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения с БД: {e}")

            # Принимаем событие закрытия
            event.accept()
        else:
            logger.info("Пользователь отменил выход из приложения")
            # Игнорируем событие закрытия (окно остается открытым)
            event.ignore()

    def setup_connections(self):
        logger.debug("Настройка подключений сигналов и слотов")
        # Специальные обработчики
        self.ui.table_clients.cellDoubleClicked.connect(self.on_client_double_click)
        self.ui.table_clients.cellClicked.connect(self.on_client_cell_click)
        self.ui.table_employees.cellDoubleClicked.connect(self.on_employee_double_click)
        self.ui.table_employees.cellClicked.connect(self.on_employee_cell_click)
        self.ui.table_projects.cellDoubleClicked.connect(self.on_project_double_click)
        self.ui.table_projects.cellClicked.connect(self.on_project_cell_click)
        self.ui.table_tasks.cellDoubleClicked.connect(self.on_task_double_click)
        self.ui.table_tasks.cellClicked.connect(self.on_task_cell_click)
        self.ui.date_project_start.dateChanged.connect(self.on_project_date_changed)
        self.ui.date_project_end.dateChanged.connect(self.on_project_date_changed)

        # Кнопки добавления
        self.ui.btn_add_client.clicked.connect(self.add_client)
        self.ui.btn_add_employee.clicked.connect(self.add_employee)
        self.ui.btn_add_project.clicked.connect(self.add_project)
        self.ui.btn_add_task.clicked.connect(self.add_task)

        # Кнопки удаления
        self.ui.btn_delete_client.clicked.connect(self.delete_client)
        self.ui.btn_delete_employee.clicked.connect(self.delete_employee)
        self.ui.btn_delete_project.clicked.connect(self.delete_project)
        self.ui.btn_delete_task.clicked.connect(self.delete_task)

        # Поиск
        self.ui.line_search_client.textChanged.connect(self.search_clients)
        self.ui.line_search_employee.textChanged.connect(self.search_employees)
        self.ui.line_search_project.textChanged.connect(self.search_projects)
        self.ui.line_search_task.textChanged.connect(self.search_tasks)

        # Excel
        self.ui.btn_import_excel.clicked.connect(self.import_from_excel)
        self.ui.btn_export_excel.clicked.connect(self.export_to_excel)

        # Отчеты
        self.ui.btn_generate_pdf_simple.clicked.connect(self.generate_pdf_simple)

        # Создаем меню отчетов из ТЗ
        menubar = self.menuBar()
        reports_menu = menubar.addMenu("📊 Отчеты")

        # Отчет: Проекты для клиента
        action_projects_by_client = reports_menu.addAction("Проекты для клиента")
        action_projects_by_client.triggered.connect(self.report_projects_by_client)

        # Отчет: Проекты с нарушением сроков
        action_overdue_projects = reports_menu.addAction("Проекты с нарушением сроков")
        action_overdue_projects.triggered.connect(self.report_overdue_projects)

        # Отчет: Сотрудники на проекте
        action_employees_on_project = reports_menu.addAction("Сотрудники, занятые на проекте")
        action_employees_on_project.triggered.connect(self.report_employees_on_project)

        # Отчет: Загрузка сотрудника
        action_employee_workload = reports_menu.addAction("Загрузка сотрудника")
        action_employee_workload.triggered.connect(self.report_employee_workload)

        logger.debug("Все подключения настроены")

    def load_all_data(self):
        logger.info("Загрузка всех данных")
        self.load_clients()
        self.load_employees()
        self.load_projects()
        self.load_tasks()
        logger.info("Все данные загружены")

    def on_employee_cell_click(self, row, column):
        # Обработка клика на ячейку сотрудника - показ информации при клике на ID
        if column == 0:  # Колонка ID
            try:
                employee_id = self.ui.table_employees.item(row, 0).text()
                employee_name = self.ui.table_employees.item(row, 1).text()
                employee_position = self.ui.table_employees.item(row, 2).text()

                logger.info(f"Просмотр информации о сотруднике: ID={employee_id}, Имя={employee_name}")

                info_message = f"""
👤 Детальная информация о сотруднике:

ID: {employee_id}
Имя: {employee_name}
Должность: {employee_position}
                """

                QMessageBox.information(
                    self,
                    "Информация о сотруднике",
                    info_message
                )
            except Exception as e:
                logger.error(f"Не удалось загрузить информацию о сотруднике: {e}")
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить информацию: {e}")

    def on_employee_double_click(self, row, column):
        logger.debug(f"Двойной клик по сотруднику: строка={row}, колонка={column}")
        try:
            employee_id = self.ui.table_employees.item(row, 0).text()
            employee_name = self.ui.table_employees.item(row, 1).text()
            employee_position = self.ui.table_employees.item(row, 2).text()

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать сотрудника #{employee_id}")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout()

            layout.addWidget(QLabel("Имя сотрудника:"))
            name_edit = QLineEdit(employee_name)
            layout.addWidget(name_edit)

            layout.addWidget(QLabel("Должность:"))
            position_edit = QLineEdit(employee_position)
            layout.addWidget(position_edit)

            button_layout = QHBoxLayout()
            btn_save = QPushButton("Сохранить")
            btn_cancel = QPushButton("Отмена")
            button_layout.addWidget(btn_save)
            button_layout.addWidget(btn_cancel)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def save_changes():
                try:
                    new_name = name_edit.text().strip()
                    new_position = position_edit.text().strip()

                    new_name, new_position = Validator.validate_employee_data(new_name, new_position)

                    # Проверка уникальности имени (исключая текущего сотрудника)
                    Validator.check_employee_name_uniqueness(new_name, cursor, exclude_id=employee_id)

                    cursor.execute(
                        "UPDATE employee SET employee_name = %s, employee_position = %s WHERE employee_id = %s",
                        (new_name, new_position, employee_id)
                    )
                    conn.commit()
                    logger.info(f"Сотрудник ID={employee_id} успешно обновлен")

                    QMessageBox.information(dialog, "Успех", "Данные сотрудника обновлены!")
                    dialog.accept()
                    self.load_employees()

                except ValidationError as e:
                    QMessageBox.warning(dialog, "Ошибка валидации", str(e))
                except Exception as e:
                    logger.error(f"Ошибка обновления сотрудника: {e}")
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка обновления: {e}")

            btn_save.clicked.connect(save_changes)
            btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

        except Exception as e:
            logger.error(f"Не удалось открыть редактирование сотрудника: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть редактирование: {e}")

    def on_project_cell_click(self, row, column):
        # Обработка клика на ячейку проекта - показ информации при клике на ID проекта или клиента
        try:
            if column == 0:  # Колонка ID проекта
                project_id = self.ui.table_projects.item(row, 0).text()
                project_name = self.ui.table_projects.item(row, 1).text()
                client_id = self.ui.table_projects.item(row, 2).text()
                project_start = self.ui.table_projects.item(row, 3).text()
                project_end = self.ui.table_projects.item(row, 4).text()

                # Получаем имя клиента
                cursor.execute(
                    "SELECT client_name FROM clients WHERE client_id = %s",
                    (client_id,)
                )
                result = cursor.fetchone()
                client_name = result[0] if result else "Не найден"

                # Подсчитываем задачи проекта
                cursor.execute(
                    "SELECT COUNT(*) FROM task WHERE task_project = %s",
                    (project_id,)
                )
                task_count = cursor.fetchone()[0]

                # Получаем задачи
                cursor.execute(
                    "SELECT task_description, task_status FROM task WHERE task_project = %s",
                    (project_id,)
                )
                tasks = cursor.fetchall()
                task_list = "\n  • " + "\n  • ".join([f"{t[0]} [{t[1]}]" for t in tasks]) if tasks else "  Нет задач"

                logger.info(f"Просмотр информации о проекте: ID={project_id}, Название={project_name}")

                info_message = f"""
📁 Детальная информация о проекте:

ID проекта: {project_id}
Название: {project_name}
Клиент: {client_name} (ID: {client_id})
Период: {project_start} — {project_end}
Количество задач: {task_count}

Задачи:
{task_list}
                """

                QMessageBox.information(
                    self,
                    "Информация о проекте",
                    info_message
                )

            elif column == 2:  # Колонка ID клиента - смена клиента проекта
                project_id = self.ui.table_projects.item(row, 0).text()
                current_client_id = self.ui.table_projects.item(row, 2).text()

                # Получаем всех клиентов
                cursor.execute("SELECT client_id, client_name, client_contact FROM clients")
                clients = cursor.fetchall()

                if not clients:
                    QMessageBox.warning(self, "Ошибка", "Нет доступных клиентов")
                    return

                # Создаем диалог выбора клиента
                from PySide6.QtWidgets import QInputDialog
                client_names = [f"{c[1]} (ID: {c[0]})" for c in clients]
                current_index = next((i for i, c in enumerate(clients) if str(c[0]) == current_client_id), 0)

                client_str, ok = QInputDialog.getItem(
                    self,
                    "Сменить клиента проекта",
                    "Выберите нового клиента для проекта:",
                    client_names,
                    current_index,
                    False
                )

                if not ok:
                    return

                new_client_id = clients[client_names.index(client_str)][0]

                # Обновляем клиента проекта
                try:
                    cursor.execute(
                        "UPDATE project SET project_client = %s WHERE project_id = %s",
                        (new_client_id, project_id)
                    )
                    conn.commit()
                    logger.info(f"Клиент проекта ID={project_id} изменен на {new_client_id}")
                    QMessageBox.information(self, "Успех", "Клиент проекта изменен!")
                    self.load_projects()
                except Exception as e:
                    logger.error(f"Ошибка смены клиента: {e}")
                    QMessageBox.critical(self, "Ошибка", str(e))

        except Exception as e:
            logger.error(f"Не удалось загрузить информацию: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить информацию: {e}")

    def on_project_double_click(self, row, column):
        logger.debug(f"Двойной клик по проекту: строка={row}, колонка={column}")
        try:
            from PySide6.QtCore import QDate
            project_id = self.ui.table_projects.item(row, 0).text()
            project_name = self.ui.table_projects.item(row, 1).text()
            project_client = self.ui.table_projects.item(row, 2).text()
            project_start = self.ui.table_projects.item(row, 3).text()
            project_end = self.ui.table_projects.item(row, 4).text()

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать проект #{project_id}")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout()

            layout.addWidget(QLabel("Название проекта:"))
            name_edit = QLineEdit(project_name)
            layout.addWidget(name_edit)

            layout.addWidget(QLabel("Дата начала:"))
            start_date_edit = QDateEdit()
            start_date_edit.setCalendarPopup(True)
            start_date_edit.setDate(QDate.fromString(project_start, "yyyy-MM-dd"))
            layout.addWidget(start_date_edit)

            layout.addWidget(QLabel("Дата окончания:"))
            end_date_edit = QDateEdit()
            end_date_edit.setCalendarPopup(True)
            end_date_edit.setDate(QDate.fromString(project_end, "yyyy-MM-dd"))
            layout.addWidget(end_date_edit)

            button_layout = QHBoxLayout()
            btn_save = QPushButton("Сохранить")
            btn_cancel = QPushButton("Отмена")
            button_layout.addWidget(btn_save)
            button_layout.addWidget(btn_cancel)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def save_changes():
                try:
                    new_name = name_edit.text().strip()
                    new_start = start_date_edit.date()
                    new_end = end_date_edit.date()

                    new_name, new_start, new_end = Validator.validate_project_data(new_name, new_start, new_end)

                    cursor.execute(
                        "UPDATE project SET project_name = %s, project_start_date = %s, project_end_date = %s WHERE project_id = %s",
                        (new_name, new_start.toString("yyyy-MM-dd"), new_end.toString("yyyy-MM-dd"), project_id)
                    )
                    conn.commit()
                    logger.info(f"Проект ID={project_id} успешно обновлен")

                    QMessageBox.information(dialog, "Успех", "Данные проекта обновлены!")
                    dialog.accept()
                    self.load_projects()

                except ValidationError as e:
                    QMessageBox.warning(dialog, "Ошибка валидации", str(e))
                except Exception as e:
                    logger.error(f"Ошибка обновления проекта: {e}")
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка обновления: {e}")

            btn_save.clicked.connect(save_changes)
            btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

        except Exception as e:
            logger.error(f"Не удалось открыть редактирование проекта: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть редактирование: {e}")

    def on_task_cell_click(self, row, column):
        # Обработка клика на ячейку задачи - показ информации при клике на ID задачи или проекта
        try:
            from PySide6.QtCore import QDate

            if column == 0:  # Колонка ID задачи
                task_id = self.ui.table_tasks.item(row, 0).text()
                task_description = self.ui.table_tasks.item(row, 1).text()
                project_id = self.ui.table_tasks.item(row, 2).text()
                due_date_str = self.ui.table_tasks.item(row, 3).text()
                task_status = self.ui.table_tasks.item(row, 4).text()

                # Получаем название проекта и назначенного сотрудника
                cursor.execute("""
                               SELECT p.project_name, e.employee_name, e.employee_position
                               FROM task t
                                        LEFT JOIN project p ON t.task_project = p.project_id
                                        LEFT JOIN employee e ON t.task_assigned_employee = e.employee_id
                               WHERE t.task_id = %s
                               """, (task_id,))
                result = cursor.fetchone()

                if result:
                    project_name = result[0] if result[0] else "Не определен"
                    employee_name = result[1] if result[1] else "Не назначен"
                    employee_position = result[2] if result[2] else ""
                else:
                    project_name = "Не определен"
                    employee_name = "Не назначен"
                    employee_position = ""

                # Вычисляем оставшееся время
                due_date = QDate.fromString(due_date_str, "yyyy-MM-dd")
                current_date = QDate.currentDate()
                days_remaining = current_date.daysTo(due_date)

                if days_remaining < 0:
                    time_status = f"⚠️ ПРОСРОЧЕНО на {abs(days_remaining)} дн."
                elif days_remaining == 0:
                    time_status = "⚠️ СРОЧНО! Дедлайн сегодня!"
                elif days_remaining <= 3:
                    time_status = f"⚠️ Осталось {days_remaining} дн. (срочно)"
                else:
                    time_status = f"✓ Осталось {days_remaining} дн."

                # Форматируем информацию о сотруднике
                if employee_name != "Не назначен":
                    employee_info = f"{employee_name} ({employee_position})"
                else:
                    employee_info = "⚠️ Не назначен"

                logger.info(f"Просмотр информации о задаче: ID={task_id}")

                info_message = f"""
📋 Детальная информация о задаче:

ID задачи: {task_id}
Описание: {task_description}
Проект: {project_name} (ID: {project_id})
Дедлайн: {due_date.toString('dd.MM.yyyy')}
{time_status}
Статус: {task_status}
Исполнитель: {employee_info}
                """

                QMessageBox.information(
                    self,
                    "Информация о задаче",
                    info_message
                )

            elif column == 2:  # Колонка ID проекта - смена проекта задачи
                task_id = self.ui.table_tasks.item(row, 0).text()
                current_project_id = self.ui.table_tasks.item(row, 2).text()
                task_due_date_str = self.ui.table_tasks.item(row, 3).text()

                # Получаем все проекты
                cursor.execute("SELECT project_id, project_name, project_end_date FROM project")
                projects = cursor.fetchall()

                if not projects:
                    QMessageBox.warning(self, "Ошибка", "Нет доступных проектов")
                    return

                # Создаем диалог выбора проекта
                from PySide6.QtWidgets import QInputDialog
                project_names = [f"{p[1]} (ID: {p[0]})" for p in projects]
                current_index = next((i for i, p in enumerate(projects) if str(p[0]) == current_project_id), 0)

                project_str, ok = QInputDialog.getItem(
                    self,
                    "Сменить проект задачи",
                    "Выберите новый проект для задачи:",
                    project_names,
                    current_index,
                    False
                )

                if not ok:
                    return

                new_project_id = projects[project_names.index(project_str)][0]
                new_project_end = projects[project_names.index(project_str)][2]

                # Проверяем срок задачи относительно нового проекта
                from PySide6.QtCore import QDate
                task_due_date = QDate.fromString(task_due_date_str, "yyyy-MM-dd")
                project_end_str = new_project_end.strftime("%Y-%m-%d") if hasattr(new_project_end, 'strftime') else str(
                    new_project_end)

                if task_due_date.toString("yyyy-MM-dd") > project_end_str:
                    QMessageBox.warning(
                        self,
                        "Ошибка срока",
                        f"Срок задачи ({task_due_date.toString('dd.MM.yyyy')}) позже окончания проекта ({project_end_str})!\n"
                        "Смена проекта невозможна."
                    )
                    return

                # Обновляем проект задачи
                try:
                    cursor.execute(
                        "UPDATE task SET task_project = %s WHERE task_id = %s",
                        (new_project_id, task_id)
                    )
                    conn.commit()
                    logger.info(f"Проект задачи ID={task_id} изменен на {new_project_id}")
                    QMessageBox.information(self, "Успех", "Проект задачи изменен!")
                    self.load_tasks()
                except Exception as e:
                    logger.error(f"Ошибка смены проекта: {e}")
                    QMessageBox.critical(self, "Ошибка", str(e))

        except Exception as e:
            logger.error(f"Не удалось загрузить информацию: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить информацию: {e}")

    def on_task_double_click(self, row, column):
        logger.debug(f"Двойной клик по задаче: строка={row}, колонка={column}")
        try:
            from PySide6.QtCore import QDate
            from PySide6.QtWidgets import QComboBox

            task_id = self.ui.table_tasks.item(row, 0).text()
            task_description = self.ui.table_tasks.item(row, 1).text()
            task_project = self.ui.table_tasks.item(row, 2).text()
            task_due = self.ui.table_tasks.item(row, 3).text()
            task_status = self.ui.table_tasks.item(row, 4).text()

            # Быстрое редактирование описания (колонка 1)
            if column == 1:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Редактировать описание задачи #{task_id}")
                dialog.setMinimumWidth(400)

                layout = QVBoxLayout()
                layout.addWidget(QLabel("Новое описание:"))
                desc_edit = QLineEdit(task_description)
                layout.addWidget(desc_edit)

                button_layout = QHBoxLayout()
                btn_save = QPushButton("Сохранить")
                btn_cancel = QPushButton("Отмена")
                button_layout.addWidget(btn_save)
                button_layout.addWidget(btn_cancel)
                layout.addLayout(button_layout)

                dialog.setLayout(layout)

                def save_desc():
                    try:
                        new_desc = desc_edit.text().strip()
                        if not new_desc:
                            QMessageBox.warning(dialog, "Ошибка", "Описание не может быть пустым")
                            return

                        cursor.execute(
                            "UPDATE task SET task_description = %s WHERE task_id = %s",
                            (new_desc, task_id)
                        )
                        conn.commit()
                        logger.info(f"Описание задачи ID={task_id} обновлено")
                        QMessageBox.information(dialog, "Успех", "Описание обновлено!")
                        dialog.accept()
                        self.load_tasks()
                    except Exception as e:
                        logger.error(f"Ошибка обновления описания: {e}")
                        QMessageBox.critical(dialog, "Ошибка", str(e))

                btn_save.clicked.connect(save_desc)
                btn_cancel.clicked.connect(dialog.reject)
                dialog.exec()
                return

            # Быстрое редактирование статуса (колонка 4)
            elif column == 4:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Изменить статус задачи #{task_id}")
                dialog.setMinimumWidth(300)

                layout = QVBoxLayout()
                layout.addWidget(QLabel("Выберите новый статус:"))

                status_combo = QComboBox()
                statuses = [
                    ("in progress", "⏳ В работе"),
                    ("completed", "✓ Завершено"),
                    ("pending", "⏸ Ожидает"),
                    ("cancelled", "✗ Отменено")
                ]

                for status_val, status_label in statuses:
                    status_combo.addItem(status_label, status_val)
                    if task_status == status_val:
                        status_combo.setCurrentText(status_label)

                layout.addWidget(status_combo)

                button_layout = QHBoxLayout()
                btn_save = QPushButton("Сохранить")
                btn_cancel = QPushButton("Отмена")
                button_layout.addWidget(btn_save)
                button_layout.addWidget(btn_cancel)
                layout.addLayout(button_layout)

                dialog.setLayout(layout)

                def save_status():
                    try:
                        new_status = status_combo.currentData()
                        cursor.execute(
                            "UPDATE task SET task_status = %s WHERE task_id = %s",
                            (new_status, task_id)
                        )
                        conn.commit()
                        logger.info(f"Статус задачи ID={task_id} изменен на {new_status}")
                        QMessageBox.information(dialog, "Успех", "Статус обновлен!")
                        dialog.accept()
                        self.load_tasks()
                    except Exception as e:
                        logger.error(f"Ошибка обновления статуса: {e}")
                        QMessageBox.critical(dialog, "Ошибка", str(e))

                btn_save.clicked.connect(save_status)
                btn_cancel.clicked.connect(dialog.reject)
                dialog.exec()
                return

            # Редактирование срока и всего остального кроме исполнителя (колонка 3)
            elif column == 3:
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Редактировать задачу #{task_id}")
                dialog.setMinimumWidth(400)

                layout = QVBoxLayout()

                layout.addWidget(QLabel("Описание задачи:"))
                desc_edit = QLineEdit(task_description)
                layout.addWidget(desc_edit)

                layout.addWidget(QLabel("Срок выполнения:"))
                due_date_edit = QDateEdit()
                due_date_edit.setCalendarPopup(True)
                due_date_edit.setDate(QDate.fromString(task_due, "yyyy-MM-dd"))
                layout.addWidget(due_date_edit)

                # Добавляем выбор проекта
                layout.addWidget(QLabel("Проект:"))
                project_combo = QComboBox()

                cursor.execute("SELECT project_id, project_name FROM project")
                projects = cursor.fetchall()
                selected_project_index = 0
                for idx, proj in enumerate(projects):
                    proj_id, proj_name = proj
                    project_combo.addItem(f"{proj_name} (ID: {proj_id})", proj_id)
                    if str(proj_id) == task_project:
                        selected_project_index = idx

                project_combo.setCurrentIndex(selected_project_index)
                layout.addWidget(project_combo)

                button_layout = QHBoxLayout()
                btn_save = QPushButton("Сохранить")
                btn_cancel = QPushButton("Отмена")
                button_layout.addWidget(btn_save)
                button_layout.addWidget(btn_cancel)
                layout.addLayout(button_layout)

                dialog.setLayout(layout)

                def save_task_without_employee():
                    try:
                        new_desc = desc_edit.text().strip()
                        new_due = due_date_edit.date()
                        new_project = project_combo.currentData()

                        # Валидация с новым проектом
                        new_desc, new_due = Validator.validate_task_data(new_desc, new_due, int(new_project))

                        cursor.execute(
                            "UPDATE task SET task_description = %s, task_due_date = %s, task_project = %s WHERE task_id = %s",
                            (new_desc, new_due.toString("yyyy-MM-dd"), new_project, task_id)
                        )
                        conn.commit()
                        logger.info(f"Задача ID={task_id} обновлена (без изменения исполнителя)")
                        QMessageBox.information(dialog, "Успех", "Задача обновлена!")
                        dialog.accept()
                        self.load_tasks()
                    except ValidationError as e:
                        QMessageBox.warning(dialog, "Ошибка валидации", str(e))
                    except Exception as e:
                        logger.error(f"Ошибка обновления задачи: {e}")
                        QMessageBox.critical(dialog, "Ошибка", str(e))

                btn_save.clicked.connect(save_task_without_employee)
                btn_cancel.clicked.connect(dialog.reject)
                dialog.exec()
                return

            # Быстрое переназначение исполнителя (колонка 5)
            elif column == 5:
                # Получаем текущего исполнителя
                cursor.execute("SELECT task_assigned_employee FROM task WHERE task_id = %s", (task_id,))
                current_employee = cursor.fetchone()[0]

                dialog = QDialog(self)
                dialog.setWindowTitle(f"Переназначить исполнителя задачи #{task_id}")
                dialog.setMinimumWidth(350)

                layout = QVBoxLayout()
                layout.addWidget(QLabel("Выберите нового исполнителя:"))

                employee_combo = QComboBox()
                employee_combo.addItem("-- Без назначения --", None)

                cursor.execute("SELECT employee_id, employee_name, employee_position FROM employee")
                employees = cursor.fetchall()
                selected_index = 0
                for idx, emp in enumerate(employees, 1):
                    emp_id, emp_name, emp_pos = emp
                    employee_combo.addItem(f"{emp_name} - {emp_pos}", emp_id)
                    if current_employee == emp_id:
                        selected_index = idx

                employee_combo.setCurrentIndex(selected_index)
                layout.addWidget(employee_combo)

                button_layout = QHBoxLayout()
                btn_save = QPushButton("Сохранить")
                btn_cancel = QPushButton("Отмена")
                button_layout.addWidget(btn_save)
                button_layout.addWidget(btn_cancel)
                layout.addLayout(button_layout)

                dialog.setLayout(layout)

                def save_employee():
                    try:
                        new_employee = employee_combo.currentData()
                        cursor.execute(
                            "UPDATE task SET task_assigned_employee = %s WHERE task_id = %s",
                            (new_employee, task_id)
                        )
                        conn.commit()
                        logger.info(f"Исполнитель задачи ID={task_id} изменен")
                        QMessageBox.information(dialog, "Успех", "Исполнитель переназначен!")
                        dialog.accept()
                        self.load_tasks()
                    except Exception as e:
                        logger.error(f"Ошибка переназначения исполнителя: {e}")
                        QMessageBox.critical(dialog, "Ошибка", str(e))

                btn_save.clicked.connect(save_employee)
                btn_cancel.clicked.connect(dialog.reject)
                dialog.exec()
                return

            # Полное редактирование (другие колонки) - описание, срок, исполнитель
            # Получаем текущего назначенного сотрудника
            cursor.execute("SELECT task_assigned_employee FROM task WHERE task_id = %s", (task_id,))
            current_employee = cursor.fetchone()[0]

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Редактировать задачу #{task_id}")
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout()

            layout.addWidget(QLabel("Описание задачи:"))
            desc_edit = QLineEdit(task_description)
            layout.addWidget(desc_edit)

            layout.addWidget(QLabel("Срок выполнения:"))
            due_date_edit = QDateEdit()
            due_date_edit.setCalendarPopup(True)
            due_date_edit.setDate(QDate.fromString(task_due, "yyyy-MM-dd"))
            layout.addWidget(due_date_edit)

            # Добавляем выбор сотрудника
            layout.addWidget(QLabel("Исполнитель:"))
            employee_combo = QComboBox()
            employee_combo.addItem("-- Без назначения --", None)

            cursor.execute("SELECT employee_id, employee_name, employee_position FROM employee")
            employees = cursor.fetchall()
            selected_index = 0
            for idx, emp in enumerate(employees, 1):
                emp_id, emp_name, emp_pos = emp
                employee_combo.addItem(f"{emp_name} - {emp_pos}", emp_id)
                if current_employee == emp_id:
                    selected_index = idx

            employee_combo.setCurrentIndex(selected_index)
            layout.addWidget(employee_combo)

            button_layout = QHBoxLayout()
            btn_save = QPushButton("Сохранить")
            btn_cancel = QPushButton("Отмена")
            button_layout.addWidget(btn_save)
            button_layout.addWidget(btn_cancel)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def save_changes():
                try:
                    new_desc = desc_edit.text().strip()
                    new_due = due_date_edit.date()
                    new_employee = employee_combo.currentData()

                    new_desc, new_due = Validator.validate_task_data(new_desc, new_due, int(task_project))

                    cursor.execute(
                        "UPDATE task SET task_description = %s, task_due_date = %s, task_assigned_employee = %s WHERE task_id = %s",
                        (new_desc, new_due.toString("yyyy-MM-dd"), new_employee, task_id)
                    )
                    conn.commit()
                    logger.info(f"Задача ID={task_id} успешно обновлена")

                    dialog.accept()
                    self.load_tasks()

                except ValidationError as e:
                    QMessageBox.warning(dialog, "Ошибка валидации", str(e))
                except Exception as e:
                    logger.error(f"Ошибка обновления задачи: {e}")
                    QMessageBox.critical(dialog, "Ошибка", f"Ошибка обновления: {e}")

            btn_save.clicked.connect(save_changes)
            btn_cancel.clicked.connect(dialog.reject)

            dialog.exec()

        except Exception as e:
            logger.error(f"Не удалось открыть редактирование задачи: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть редактирование: {e}")

    def load_clients(self):
        logger.debug("Загрузка клиентов из БД")
        try:
            cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()
            self.ui.table_clients.setRowCount(len(clients))
            for row_idx, client in enumerate(clients):
                for col_idx, value in enumerate(client):
                    self.ui.table_clients.setItem(row_idx, col_idx,
                                                  QTableWidgetItem(str(value)))
            self.ui.table_clients.resizeColumnsToContents()
            logger.info(f"Загружено клиентов: {len(clients)}")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка загрузки клиентов: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки клиентов: {err}")

    def load_employees(self):
        logger.debug("Загрузка сотрудников из БД")
        try:
            cursor.execute("SELECT * FROM employee")
            employees = cursor.fetchall()

            self.ui.table_employees.setRowCount(len(employees))
            for row_idx, employee in enumerate(employees):
                for col_idx, value in enumerate(employee):
                    self.ui.table_employees.setItem(row_idx, col_idx,
                                                    QTableWidgetItem(str(value)))
            self.ui.table_employees.resizeColumnsToContents()
            logger.info(f"Загружено сотрудников: {len(employees)}")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка загрузки сотрудников: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки сотрудников: {err}")

    def load_projects(self):
        logger.debug("Загрузка проектов из БД")
        try:
            cursor.execute("SELECT * FROM project")
            projects = cursor.fetchall()

            self.ui.table_projects.setRowCount(len(projects))
            for row_idx, project in enumerate(projects):
                for col_idx, value in enumerate(project):
                    self.ui.table_projects.setItem(row_idx, col_idx,
                                                   QTableWidgetItem(str(value)))
            self.ui.table_projects.resizeColumnsToContents()
            logger.info(f"Загружено проектов: {len(projects)}")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка загрузки проектов: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки проектов: {err}")

    def load_tasks(self):
        logger.debug("Загрузка задач из БД")
        try:
            cursor.execute("""
                           SELECT t.task_id,
                                  t.task_description,
                                  t.task_project,
                                  t.task_due_date,
                                  t.task_status,
                                  COALESCE(e.employee_name, 'Не назначен') as employee
                           FROM task t
                                    LEFT JOIN employee e ON t.task_assigned_employee = e.employee_id
                           """)
            tasks = cursor.fetchall()
            self.ui.table_tasks.setRowCount(len(tasks))
            for row_idx, task in enumerate(tasks):
                for col_idx, value in enumerate(task):
                    self.ui.table_tasks.setItem(row_idx, col_idx,
                                                QTableWidgetItem(str(value)))
            self.ui.table_tasks.resizeColumnsToContents()
            logger.info(f"Загружено задач: {len(tasks)}")
        except mysql.connector.Error as err:
            logger.error(f"Ошибка загрузки задач: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки задач: {err}")

    def add_client(self):
        logger.debug("Попытка добавления клиента")
        try:
            name = self.ui.line_client_name.text()
            contact = self.ui.line_client_contact.text()
            logger.debug(f"Введенные данные клиента: имя={name}, контакт={contact}")

            # Валидация
            name, contact = Validator.validate_client_data(name, contact)
            logger.debug("Валидация данных клиента пройдена")

            # Проверка уникальности email
            Validator.check_email_uniqueness(contact, cursor)
            logger.debug("Проверка уникальности email пройдена")

            client = Client(name=name, contact=contact)
            if client.save_to_db():
                QMessageBox.information(self, "Успех",
                                        f"Клиент '{name}' успешно добавлен!\nEmail: {contact}")
                self.ui.line_client_name.clear()
                self.ui.line_client_contact.clear()
                self.load_clients()
            else:
                raise DatabaseError("добавление клиента", "Неизвестная ошибка")
        except InvalidEmailError as e:
            logger.warning(f"Ошибка валидации email: {e}")
            QMessageBox.warning(self, "Ошибка Email", str(e))
        except ValidationError as e:
            logger.warning(f"Ошибка валидации данных клиента: {e}")
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except DatabaseError as e:
            logger.error(f"Ошибка базы данных при добавлении клиента: {e}")
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при добавлении клиента: {e}")
            QMessageBox.critical(self, "Непредвиденная ошибка", str(e))

    def add_employee(self):
        logger.debug("Попытка добавления сотрудника")
        try:
            name = self.ui.line_employee_name.text().strip()
            position = self.ui.line_employee_position.text().strip()
            logger.debug(f"Введенные данные сотрудника: имя={name}, должность={position}")

            name, position = Validator.validate_employee_data(name, position)
            logger.debug("Валидация данных сотрудника пройдена")

            # Проверка уникальности имени сотрудника
            Validator.check_employee_name_uniqueness(name, cursor)
            logger.debug("Проверка уникальности имени сотрудника пройдена")

            employee = Employee(name=name, position=position)
            if employee.save_to_db():
                QMessageBox.information(self, "Успех",
                                        f"Сотрудник '{name}' успешно добавлен!")
                self.ui.line_employee_name.clear()
                self.ui.line_employee_position.clear()
                self.load_employees()
            else:
                raise DatabaseError("добавление сотрудника", "Неизвестная ошибка")

        except ValidationError as e:
            logger.warning(f"Ошибка валидации данных сотрудника: {e}")
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except DatabaseError as e:
            logger.error(f"Ошибка базы данных при добавлении сотрудника: {e}")
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при добавлении сотрудника: {e}")
            QMessageBox.critical(self, "Непредвиденная ошибка", str(e))

    def add_project(self):
        logger.debug("Попытка добавления проекта")
        try:
            from PySide6.QtCore import QDate
            from PySide6.QtWidgets import QInputDialog

            name = self.ui.line_project_name.text().strip()
            start_date = self.ui.date_project_start.date()
            end_date = self.ui.date_project_end.date()
            logger.debug(
                f"Введенные данные проекта: название={name}, начало={start_date.toString('yyyy-MM-dd')}, конец={end_date.toString('yyyy-MM-dd')}")

            name, start_date, end_date = Validator.validate_project_data(name, start_date, end_date)
            logger.debug("Валидация данных проекта пройдена")

            # Проверяем наличие клиентов
            cursor.execute("SELECT client_id, client_name FROM clients")
            clients = cursor.fetchall()
            if not clients:
                logger.warning("Попытка добавить проект без существующих клиентов")
                QMessageBox.warning(self, "Предупреждение",
                                    "Сначала добавьте хотя бы одного клиента!")
                return

            # Выбор клиента
            client_names = [f"{c[1]} (ID: {c[0]})" for c in clients]
            client_str, ok = QInputDialog.getItem(
                self,
                "Выбор клиента",
                "Выберите клиента для проекта:",
                client_names,
                0,
                False
            )

            if not ok:
                logger.debug("Пользователь отменил выбор клиента")
                return

            client_id = clients[client_names.index(client_str)][0]
            logger.debug(f"Выбран клиент ID={client_id}")

            project = Project(
                name=name,
                client_id=client_id,
                start_date=start_date.toString("yyyy-MM-dd"),
                end_date=end_date.toString("yyyy-MM-dd")
            )
            if project.save_to_db():
                QMessageBox.information(self, "Успех",
                                        f"Проект '{name}' успешно добавлен для клиента!")
                self.ui.line_project_name.clear()
                self.load_projects()
            else:
                raise DatabaseError("добавление проекта", "Неизвестная ошибка")
        except ValidationError as e:
            logger.warning(f"Ошибка валидации данных проекта: {e}")
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except DatabaseError as e:
            logger.error(f"Ошибка базы данных при добавлении проекта: {e}")
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при добавлении проекта: {e}")
            QMessageBox.critical(self, "Непредвиденная ошибка", str(e))

    def add_task(self):
        logger.debug("Попытка добавления задачи")
        try:
            from PySide6.QtCore import QDate
            from PySide6.QtWidgets import QInputDialog

            description = self.ui.line_task_description.text().strip()
            due_date = self.ui.date_task_due.date()
            logger.debug(f"Введенные данные задачи: описание={description}, срок={due_date.toString('yyyy-MM-dd')}")

            # СНАЧАЛА валидируем описание (без project_id, только проверка описания)
            description, _ = Validator.validate_task_data(description, due_date, project_id=None)
            logger.debug("Валидация описания задачи пройдена")

            # Проверяем наличие проектов
            cursor.execute("SELECT project_id, project_name FROM project")
            projects = cursor.fetchall()
            if not projects:
                logger.warning("Попытка добавить задачу без существующих проектов")
                QMessageBox.warning(self, "Предупреждение",
                                    "Сначала добавьте хотя бы один проект!")
                return

            # Выбор проекта
            project_names = [f"{p[1]} (ID: {p[0]})" for p in projects]
            project_str, ok = QInputDialog.getItem(
                self,
                "Выбор проекта",
                "Выберите проект для задачи:",
                project_names,
                0,
                False
            )

            if not ok:
                return

            project_id = projects[project_names.index(project_str)][0]
            logger.debug(f"Выбран проект ID={project_id}")

            # ПОСЛЕ ВЫБОРА ПРОЕКТА валидируем срок задачи относительно проекта
            description, due_date = Validator.validate_task_data(description, due_date, project_id)
            logger.debug("Валидация срока задачи относительно проекта пройдена")

            # Проверяем наличие сотрудников
            cursor.execute("SELECT employee_id, employee_name, employee_position FROM employee")
            employees = cursor.fetchall()

            employee_id = None
            if employees:
                # Выбор сотрудника (опционально)
                employee_names = ["-- Без назначения --"] + [f"{e[1]} - {e[2]} (ID: {e[0]})" for e in employees]
                employee_str, ok = QInputDialog.getItem(
                    self,
                    "Назначение сотрудника",
                    "Выберите исполнителя для задачи (опционально):",
                    employee_names,
                    0,
                    False
                )

                if not ok:
                    return

                if employee_str != "-- Без назначения --":
                    employee_id = employees[employee_names.index(employee_str) - 1][0]
                    logger.debug(f"Выбран сотрудник ID={employee_id}")
                else:
                    logger.debug("Задача создается без назначения сотрудника")
            else:
                logger.debug("Сотрудники отсутствуют, задача будет без назначения")

            # Вся валидация уже выполнена выше
            task = Task(
                description=description,
                project_id=project_id,
                due_date=due_date.toString("yyyy-MM-dd"),
                employee_id=employee_id
            )
            if task.save_to_db():
                QMessageBox.information(self, "Успех",
                                        f"Задача '{description}' успешно добавлена!")
                self.ui.line_task_description.clear()
                self.load_tasks()
            else:
                raise DatabaseError("добавление задачи", "Неизвестная ошибка")
        except ValidationError as e:
            logger.warning(f"Ошибка валидации данных задачи: {e}")
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except DatabaseError as e:
            logger.error(f"Ошибка базы данных при добавлении задачи: {e}")
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при добавлении задачи: {e}")
            QMessageBox.critical(self, "Непредвиденная ошибка", str(e))

    def delete_client(self):
        logger.debug("Попытка удаления клиента")
        selected_row = self.ui.table_clients.currentRow()
        if selected_row < 0:
            logger.warning("Попытка удалить клиента без выбора строки")
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите клиента для удаления!")
            return

        client_id = self.ui.table_clients.item(selected_row, 0).text()
        client_name = self.ui.table_clients.item(selected_row, 1).text()
        logger.debug(f"Выбран клиент для удаления: ID={client_id}, Имя={client_name}")

        try:
            # Проверяем наличие связанных проектов
            cursor.execute("SELECT COUNT(*) FROM project WHERE project_client = %s", (client_id,))
            project_count = cursor.fetchone()[0]

            # Проверяем наличие задач в проектах клиента
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM task t
                                    INNER JOIN project p ON t.task_project = p.project_id
                           WHERE p.project_client = %s
                           """, (client_id,))
            task_count = cursor.fetchone()[0]

            if project_count > 0 or task_count > 0:
                reply = QMessageBox.question(
                    self,
                    "Предупреждение",
                    f"У клиента '{client_name}' есть:\n"
                    f"  • Проектов: {project_count}\n"
                    f"  • Задач: {task_count}\n\n"
                    f"Удалить клиента вместе со ВСЕМИ проектами и задачами?\n"
                    f"Это действие невозможно отменить!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            else:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение удаления",
                    f"Вы действительно хотите удалить клиента '{client_name}'?\n\n"
                    f"Это действие невозможно отменить!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

            if reply == QMessageBox.Yes:
                # Удаляем в правильном порядке: задачи → проекты → клиент

                # 1. Удаляем задачи из проектов клиента
                if task_count > 0:
                    cursor.execute("""
                                   DELETE
                                   FROM task
                                   WHERE task_project IN (SELECT project_id
                                                          FROM project
                                                          WHERE project_client = %s)
                                   """, (client_id,))
                    logger.info(f"Удалено {task_count} задач(и) клиента ID={client_id}")

                # 2. Удаляем проекты клиента
                if project_count > 0:
                    cursor.execute("DELETE FROM project WHERE project_client = %s", (client_id,))
                    logger.info(f"Удалено {project_count} проект(ов) клиента ID={client_id}")

                # 3. Удаляем самого клиента
                cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
                conn.commit()

                logger.info(f"Клиент успешно удален: ID={client_id}, Имя={client_name}")

                summary = f"Клиент удален!"
                if project_count > 0 or task_count > 0:
                    summary += f"\n\nТакже удалено:"
                    if project_count > 0:
                        summary += f"\n  • Проектов: {project_count}"
                    if task_count > 0:
                        summary += f"\n  • Задач: {task_count}"

                QMessageBox.information(self, "Успех", summary)
                self.load_clients()
                self.load_projects()
                self.load_tasks()
            else:
                logger.debug(f"Удаление клиента ID={client_id} отменено пользователем")

        except mysql.connector.Error as err:
            logger.error(f"Ошибка удаления клиента ID={client_id}: {err}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {err}")

    def delete_employee(self):
        logger.debug("Попытка удаления сотрудника")
        selected_row = self.ui.table_employees.currentRow()
        if selected_row < 0:
            logger.warning("Попытка удалить сотрудника без выбора строки")
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите сотрудника для удаления!")
            return

        employee_id = self.ui.table_employees.item(selected_row, 0).text()
        employee_name = self.ui.table_employees.item(selected_row, 1).text()
        logger.debug(f"Выбран сотрудник для удаления: ID={employee_id}, Имя={employee_name}")

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить сотрудника '{employee_name}'?\n\n"
            f"Это действие невозможно отменить!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                cursor.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))
                conn.commit()
                logger.info(f"Сотрудник успешно удален: ID={employee_id}, Имя={employee_name}")
                QMessageBox.information(self, "Успех", "Сотрудник удален!")
                self.load_employees()
            except mysql.connector.Error as err:
                logger.error(f"Ошибка удаления сотрудника ID={employee_id}: {err}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {err}")
        else:
            logger.debug(f"Удаление сотрудника ID={employee_id} отменено пользователем")

    def delete_project(self):
        logger.debug("Попытка удаления проекта")
        selected_row = self.ui.table_projects.currentRow()
        if selected_row < 0:
            logger.warning("Попытка удалить проект без выбора строки")
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите проект для удаления!")
            return

        project_id = self.ui.table_projects.item(selected_row, 0).text()
        project_name = self.ui.table_projects.item(selected_row, 1).text()
        logger.debug(f"Выбран проект для удаления: ID={project_id}, Название={project_name}")

        try:
            # Проверяем наличие связанных задач
            cursor.execute("SELECT COUNT(*) FROM task WHERE task_project = %s", (project_id,))
            task_count = cursor.fetchone()[0]

            if task_count > 0:
                reply = QMessageBox.question(
                    self,
                    "Предупреждение",
                    f"У проекта '{project_name}' есть {task_count} задач(и).\n\n"
                    f"Удалить проект вместе со ВСЕМИ задачами?\n"
                    f"Это действие невозможно отменить!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
            else:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение удаления",
                    f"Вы действительно хотите удалить проект '{project_name}'?\n\n"
                    f"Это действие невозможно отменить!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

            if reply == QMessageBox.Yes:
                # Сначала удаляем все задачи проекта
                if task_count > 0:
                    cursor.execute("DELETE FROM task WHERE task_project = %s", (project_id,))
                    logger.info(f"Удалено {task_count} задач(и) проекта ID={project_id}")

                # Затем удаляем сам проект
                cursor.execute("DELETE FROM project WHERE project_id = %s", (project_id,))
                conn.commit()

                logger.info(f"Проект успешно удален: ID={project_id}, Название={project_name}")
                QMessageBox.information(self, "Успех",
                                        f"Проект удален!\n{'Также удалено задач: ' + str(task_count) if task_count > 0 else ''}")
                self.load_projects()
                self.load_tasks()  # Обновляем таблицу задач
            else:
                logger.debug(f"Удаление проекта ID={project_id} отменено пользователем")

        except mysql.connector.Error as err:
            logger.error(f"Ошибка удаления проекта ID={project_id}: {err}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {err}")

    def delete_task(self):
        logger.debug("Попытка удаления задачи")
        selected_row = self.ui.table_tasks.currentRow()
        if selected_row < 0:
            logger.warning("Попытка удалить задачу без выбора строки")
            QMessageBox.warning(self, "Предупреждение",
                                "Выберите задачу для удаления!")
            return

        task_id = self.ui.table_tasks.item(selected_row, 0).text()
        task_desc = self.ui.table_tasks.item(selected_row, 1).text()
        logger.debug(f"Выбрана задача для удаления: ID={task_id}, Описание={task_desc}")

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы действительно хотите удалить задачу '{task_desc}'?\n\n"
            f"Это действие невозможно отменить!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                cursor.execute("DELETE FROM task WHERE task_id = %s", (task_id,))
                conn.commit()
                logger.info(f"Задача успешно удалена: ID={task_id}, Описание={task_desc}")
                QMessageBox.information(self, "Успех", "Задача удалена!")
                self.load_tasks()
            except mysql.connector.Error as err:
                logger.error(f"Ошибка удаления задачи ID={task_id}: {err}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {err}")
        else:
            logger.debug(f"Удаление задачи ID={task_id} отменено пользователем")

    def search_clients(self):
        search_text = self.ui.line_search_client.text().strip()
        logger.debug(f"Поиск клиентов по запросу: '{search_text}'")

        if not search_text:
            logger.debug("Поисковый запрос пуст, загрузка всех клиентов")
            self.load_clients()
            return

        try:
            sql = "SELECT * FROM clients WHERE client_name LIKE %s OR client_contact LIKE %s"
            cursor.execute(sql, (f"%{search_text}%", f"%{search_text}%"))
            clients = cursor.fetchall()
            logger.info(f"Найдено клиентов по запросу '{search_text}': {len(clients)}")

            self.ui.table_clients.setRowCount(len(clients))
            for row_idx, client in enumerate(clients):
                for col_idx, value in enumerate(client):
                    self.ui.table_clients.setItem(row_idx, col_idx,
                                                  QTableWidgetItem(str(value)))
            self.ui.table_clients.resizeColumnsToContents()
        except mysql.connector.Error as err:
            logger.error(f"Ошибка поиска клиентов: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска: {err}")

    def search_employees(self):
        search_text = self.ui.line_search_employee.text().strip()
        logger.debug(f"Поиск сотрудников по запросу: '{search_text}'")

        if not search_text:
            logger.debug("Поисковый запрос пуст, загрузка всех сотрудников")
            self.load_employees()
            return

        try:
            sql = "SELECT * FROM employee WHERE employee_name LIKE %s OR employee_position LIKE %s"
            cursor.execute(sql, (f"%{search_text}%", f"%{search_text}%"))
            employees = cursor.fetchall()
            logger.info(f"Найдено сотрудников по запросу '{search_text}': {len(employees)}")

            self.ui.table_employees.setRowCount(len(employees))
            for row_idx, employee in enumerate(employees):
                for col_idx, value in enumerate(employee):
                    self.ui.table_employees.setItem(row_idx, col_idx,
                                                    QTableWidgetItem(str(value)))
            self.ui.table_employees.resizeColumnsToContents()
        except mysql.connector.Error as err:
            logger.error(f"Ошибка поиска сотрудников: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска: {err}")

    def search_projects(self):
        search_text = self.ui.line_search_project.text().strip()
        logger.debug(f"Поиск проектов по запросу: '{search_text}'")

        if not search_text:
            logger.debug("Поисковый запрос пуст, загрузка всех проектов")
            self.load_projects()
            return

        try:
            sql = "SELECT * FROM project WHERE project_name LIKE %s"
            cursor.execute(sql, (f"%{search_text}%",))
            projects = cursor.fetchall()
            logger.info(f"Найдено проектов по запросу '{search_text}': {len(projects)}")

            self.ui.table_projects.setRowCount(len(projects))
            for row_idx, project in enumerate(projects):
                for col_idx, value in enumerate(project):
                    self.ui.table_projects.setItem(row_idx, col_idx,
                                                   QTableWidgetItem(str(value)))
            self.ui.table_projects.resizeColumnsToContents()
        except mysql.connector.Error as err:
            logger.error(f"Ошибка поиска проектов: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска: {err}")

    def search_tasks(self):
        search_text = self.ui.line_search_task.text().strip()
        logger.debug(f"Поиск задач по запросу: '{search_text}'")

        if not search_text:
            logger.debug("Поисковый запрос пуст, загрузка всех задач")
            self.load_tasks()
            return

        try:
            sql = "SELECT * FROM task WHERE task_description LIKE %s OR task_status LIKE %s"
            cursor.execute(sql, (f"%{search_text}%", f"%{search_text}%"))
            tasks = cursor.fetchall()
            logger.info(f"Найдено задач по запросу '{search_text}': {len(tasks)}")

            self.ui.table_tasks.setRowCount(len(tasks))
            for row_idx, task in enumerate(tasks):
                for col_idx, value in enumerate(task):
                    self.ui.table_tasks.setItem(row_idx, col_idx,
                                                QTableWidgetItem(str(value)))
            self.ui.table_tasks.resizeColumnsToContents()
        except mysql.connector.Error as err:
            logger.error(f"Ошибка поиска задач: {err}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска: {err}")

    def export_to_excel(self):
        logger.info("Начало экспорта данных в Excel")
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить в Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            logger.debug("Экспорт в Excel отменен пользователем")
            return

        logger.debug(f"Выбран файл для экспорта: {file_path}")

        try:
            with pd.ExcelWriter(file_path) as writer:
                # Клиенты
                cursor.execute("SELECT * FROM clients")
                clients = cursor.fetchall()
                df_clients = pd.DataFrame(clients, columns=['ID', 'Имя', 'Контакт'])
                df_clients.to_excel(writer, sheet_name='Клиенты', index=False)
                logger.debug(f"Экспортировано клиентов: {len(clients)}")

                # Сотрудники
                cursor.execute("SELECT * FROM employee")
                employees = cursor.fetchall()
                df_employees = pd.DataFrame(employees, columns=['ID', 'Имя', 'Должность'])
                df_employees.to_excel(writer, sheet_name='Сотрудники', index=False)
                logger.debug(f"Экспортировано сотрудников: {len(employees)}")

                # Проекты
                cursor.execute("SELECT * FROM project")
                projects = cursor.fetchall()
                df_projects = pd.DataFrame(projects, columns=['ID', 'Название', 'Клиент', 'Начало', 'Окончание'])
                df_projects.to_excel(writer, sheet_name='Проекты', index=False)
                logger.debug(f"Экспортировано проектов: {len(projects)}")

                # Задачи - ИСПРАВЛЕНО: добавлен столбец "Исполнитель"
                cursor.execute("SELECT * FROM task")
                tasks = cursor.fetchall()
                df_tasks = pd.DataFrame(tasks, columns=['ID', 'Описание', 'Проект', 'Срок', 'Статус', 'Исполнитель'])
                df_tasks.to_excel(writer, sheet_name='Задачи', index=False)
                logger.debug(f"Экспортировано задач: {len(tasks)}")

            logger.info(f"Данные успешно экспортированы в Excel: {file_path}")
            QMessageBox.information(self, "Успех", "Данные экспортированы в Excel!")
        except Exception as e:
            logger.error(f"Ошибка экспорта в Excel: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {e}")

    def import_from_excel(self):
        logger.info("Начало импорта данных из Excel")
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть Excel", "", "Excel Files (*.xlsx)")
        if not file_path:
            logger.debug("Импорт из Excel отменен пользователем")
            return

        logger.debug(f"Выбран файл для импорта: {file_path}")

        try:
            xls = pd.ExcelFile(file_path)
            imported_counts = {'Клиенты': 0, 'Сотрудники': 0, 'Проекты': 0, 'Задачи': 0}
            error_counts = {'Клиенты': 0, 'Сотрудники': 0, 'Проекты': 0, 'Задачи': 0}

            # Клиенты
            if 'Клиенты' in xls.sheet_names:
                df_clients = pd.read_excel(xls, 'Клиенты')
                for idx, row in df_clients.iterrows():
                    try:
                        client = Client(name=row['Имя'], contact=row['Контакт'])
                        if client.save_to_db():
                            imported_counts['Клиенты'] += 1
                    except Exception as e:
                        error_counts['Клиенты'] += 1
                        logger.warning(f"Ошибка импорта клиента (строка {idx + 2}): {e}")
                logger.info(f"Импортировано клиентов: {imported_counts['Клиенты']}, ошибок: {error_counts['Клиенты']}")

            # Сотрудники
            if 'Сотрудники' in xls.sheet_names:
                df_employees = pd.read_excel(xls, 'Сотрудники')
                for idx, row in df_employees.iterrows():
                    try:
                        employee = Employee(name=row['Имя'], position=row['Должность'])
                        if employee.save_to_db():
                            imported_counts['Сотрудники'] += 1
                    except Exception as e:
                        error_counts['Сотрудники'] += 1
                        logger.warning(f"Ошибка импорта сотрудника (строка {idx + 2}): {e}")
                logger.info(
                    f"Импортировано сотрудников: {imported_counts['Сотрудники']}, ошибок: {error_counts['Сотрудники']}")

            # Проекты
            if 'Проекты' in xls.sheet_names:
                df_projects = pd.read_excel(xls, 'Проекты')
                for idx, row in df_projects.iterrows():
                    try:
                        project = Project(name=row['Название'], client_id=row['Клиент'],
                                          start_date=row['Начало'], end_date=row['Окончание'])
                        if project.save_to_db():
                            imported_counts['Проекты'] += 1
                    except Exception as e:
                        error_counts['Проекты'] += 1
                        logger.warning(f"Ошибка импорта проекта (строка {idx + 2}): {e}")
                logger.info(f"Импортировано проектов: {imported_counts['Проекты']}, ошибок: {error_counts['Проекты']}")

            # Задачи
            if 'Задачи' in xls.sheet_names:
                df_tasks = pd.read_excel(xls, 'Задачи')
                for idx, row in df_tasks.iterrows():
                    try:
                        employee_id = row.get('Исполнитель', None)
                        if pd.isna(employee_id):
                            employee_id = None
                        else:
                            employee_id = int(employee_id)
                        task = Task(description=row['Описание'], project_id=row['Проект'],
                                    due_date=row['Срок'], status=row['Статус'], employee_id=employee_id)
                        if task.save_to_db():
                            imported_counts['Задачи'] += 1
                    except Exception as e:
                        error_counts['Задачи'] += 1
                        logger.warning(f"Ошибка импорта задачи (строка {idx + 2}): {e}")
                logger.info(f"Импортировано задач: {imported_counts['Задачи']}, ошибок: {error_counts['Задачи']}")

            self.load_all_data()

            total_errors = sum(error_counts.values())
            summary = "\n".join([f"{key}: {value}" for key, value in imported_counts.items()])

            if total_errors > 0:
                logger.warning(f"Импорт завершен с ошибками. Всего ошибок: {total_errors}")
                QMessageBox.warning(self, "Импорт завершен с ошибками",
                                    f"Импортировано:\n{summary}\n\nОшибок: {total_errors}\nПодробности в project_manager.log")
            else:
                logger.info(f"Импорт успешно завершен без ошибок")
                QMessageBox.information(self, "Успех", f"Данные импортированы из Excel!\n\n{summary}")

        except Exception as e:
            logger.error(f"Критическая ошибка импорта из Excel: {e}")
            QMessageBox.critical(self, "Ошибка",
                                 f"Критическая ошибка импорта:\n{e}\n\nПроверьте структуру файла Excel.")

    def report_projects_by_client(self):
        # Отчет: Перечень проектов для определённого клиента
        logger.info("Запуск отчета: Проекты для клиента")

        from PySide6.QtWidgets import QInputDialog

        # Получаем список клиентов
        cursor.execute("SELECT client_id, client_name FROM clients ORDER BY client_name")
        clients = cursor.fetchall()

        if not clients:
            QMessageBox.warning(self, "Нет данных", "В базе нет клиентов")
            return

        client_names = [f"{c[1]} (ID: {c[0]})" for c in clients]

        client_str, ok = QInputDialog.getItem(
            self,
            "Выбор клиента",
            "Выберите клиента:",
            client_names,
            0,
            False
        )

        if ok and client_str:
            client_id = clients[client_names.index(client_str)][0]
            client_name = clients[client_names.index(client_str)][1]

            # Получаем проекты клиента
            cursor.execute(
                """SELECT project_id, project_name, project_start_date, project_end_date
                   FROM project
                   WHERE project_client = %s""",
                (client_id,)
            )
            projects = cursor.fetchall()

            if not projects:
                QMessageBox.information(
                    self,
                    "Результат",
                    f"У клиента '{client_name}' нет проектов"
                )
                return

            # Формируем отчет
            report = f"📊 ОТЧЕТ: Проекты клиента '{client_name}'\n\n"
            report += f"Всего проектов: {len(projects)}\n\n"

            for idx, proj in enumerate(projects, 1):
                report += f"{idx}. {proj[1]}\n"
                report += f"   ID: {proj[0]}\n"
                report += f"   Период: {proj[2]} — {proj[3]}\n\n"

            dialog = ReportDialog("Отчет: Проекты клиента", report, self)
            dialog.exec()
            logger.info(f"Отчет по проектам клиента {client_name} сформирован: {len(projects)} проектов")

    def report_overdue_projects(self):
        # Отчет: Проекты с нарушением сроков выполнения задач
        logger.info("Запуск отчета: Проекты с нарушением сроков")

        from PySide6.QtCore import QDate

        current_date = QDate.currentDate().toString("yyyy-MM-dd")

        # Находим проекты, в которых есть просроченные задачи
        cursor.execute(
            """SELECT DISTINCT p.project_id,
                               p.project_name,
                               p.project_end_date,
                               COUNT(t.task_id) as overdue_tasks
               FROM project p
                        INNER JOIN task t ON p.project_id = t.task_project
               WHERE t.task_due_date < %s
                 AND t.task_status != 'completed'
               GROUP BY p.project_id, p.project_name, p.project_end_date
               ORDER BY overdue_tasks DESC""",
            (current_date,)
        )
        overdue_projects = cursor.fetchall()

        if not overdue_projects:
            QMessageBox.information(
                self,
                "Отчет",
                "✅ Нет проектов с нарушением сроков!\n\nВсе задачи выполняются в срок."
            )
            return

        # Формируем отчет
        report = f"⚠️ ОТЧЕТ: Проекты с нарушением сроков\n\n"
        report += f"Всего проектов с просрочками: {len(overdue_projects)}\n\n"

        for idx, proj in enumerate(overdue_projects, 1):
            report += f"{idx}. {proj[1]} (ID: {proj[0]})\n"
            report += f"   Дедлайн проекта: {proj[2]}\n"
            report += f"   Просроченных задач: {proj[3]}\n\n"

        dialog = ReportDialog("⚠️ Отчет: Проекты с нарушением сроков", report, self)
        dialog.exec()
        logger.info(f"Отчет по просроченным проектам: {len(overdue_projects)} проектов")

    def report_employees_on_project(self):
        # Отчет: Список сотрудников, занятых на определённом проекте (через задачи)
        logger.info("Запуск отчета: Сотрудники на проекте")

        from PySide6.QtWidgets import QInputDialog

        # Получаем список проектов
        cursor.execute("SELECT project_id, project_name FROM project ORDER BY project_name")
        projects = cursor.fetchall()

        if not projects:
            QMessageBox.warning(self, "Нет данных", "В базе нет проектов")
            return

        project_names = [f"{p[1]} (ID: {p[0]})" for p in projects]

        project_str, ok = QInputDialog.getItem(
            self,
            "Выбор проекта",
            "Выберите проект:",
            project_names,
            0,
            False
        )

        if ok and project_str:
            project_id = projects[project_names.index(project_str)][0]
            project_name = projects[project_names.index(project_str)][1]

            # Получаем сотрудников, назначенных на задачи этого проекта
            cursor.execute("""
                           SELECT DISTINCT e.employee_id,
                                           e.employee_name,
                                           e.employee_position,
                                           COUNT(t.task_id)                                             as task_count,
                                           SUM(CASE WHEN t.task_status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
                           FROM employee e
                                    INNER JOIN task t ON e.employee_id = t.task_assigned_employee
                           WHERE t.task_project = %s
                           GROUP BY e.employee_id, e.employee_name, e.employee_position
                           ORDER BY e.employee_name
                           """, (project_id,))
            employees = cursor.fetchall()

            # Получаем общую статистику по проекту
            cursor.execute("SELECT COUNT(*) FROM task WHERE task_project = %s", (project_id,))
            total_tasks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM task WHERE task_project = %s AND task_assigned_employee IS NULL",
                           (project_id,))
            unassigned_tasks = cursor.fetchone()[0]

            # Формируем отчет
            report = f"""👥 ОТЧЕТ: СОТРУДНИКИ НА ПРОЕКТЕ
{'=' * 70}

📁 Проект: {project_name}
📊 Всего задач: {total_tasks}
⚠️ Без назначения: {unassigned_tasks}
👷 Назначенных сотрудников: {len(employees)}

{'=' * 70}
"""

            if employees:
                report += "\n🔹 СОТРУДНИКИ И ИХ ЗАДАЧИ:\n\n"
                for idx, emp in enumerate(employees, 1):
                    emp_id, emp_name, emp_pos, task_count, completed = emp
                    completion = (completed * 100 // task_count) if task_count > 0 else 0
                    report += f"{idx}. {emp_name} - {emp_pos}\n"
                    report += f"   Задач: {task_count} (✓ {completed}, {completion}% завершено)\n\n"
            else:
                report += "\n⚠️ На этот проект пока не назначено ни одного сотрудника\n"

            if unassigned_tasks > 0:
                report += f"\n{'=' * 70}\n"
                report += f"💡 РЕКОМЕНДАЦИЯ: Есть {unassigned_tasks} задач(а) без исполнителя.\n"
                report += f"   Назначьте сотрудников через двойной клик по задаче.\n"

            dialog = ReportDialog(f"Отчет: {project_name}", report, self)
            dialog.exec()
            logger.info(f"Отчет по сотрудникам проекта {project_name}: {len(employees)} назначенных")

    def report_employee_workload(self):
        # Отчет: Загрузка сотрудника (задачи по проектам)
        logger.info("Запуск отчета: Загрузка сотрудника")

        from PySide6.QtWidgets import QInputDialog

        # Получаем список сотрудников
        cursor.execute("SELECT employee_id, employee_name, employee_position FROM employee ORDER BY employee_name")
        employees = cursor.fetchall()

        if not employees:
            QMessageBox.warning(self, "Нет данных", "В базе нет сотрудников")
            return

        employee_names = [f"{e[1]} - {e[2]} (ID: {e[0]})" for e in employees]

        employee_str, ok = QInputDialog.getItem(
            self,
            "Выбор сотрудника",
            "Выберите сотрудника:",
            employee_names,
            0,
            False
        )

        if ok and employee_str:
            employee_id = employees[employee_names.index(employee_str)][0]
            employee_name = employees[employee_names.index(employee_str)][1]
            employee_position = employees[employee_names.index(employee_str)][2]

            # Получаем задачи сотрудника с информацией о проектах
            cursor.execute("""
                           SELECT t.task_id,
                                  t.task_description,
                                  t.task_due_date,
                                  t.task_status,
                                  p.project_name,
                                  c.client_name
                           FROM task t
                                    INNER JOIN project p ON t.task_project = p.project_id
                                    INNER JOIN clients c ON p.project_client = c.client_id
                           WHERE t.task_assigned_employee = %s
                           ORDER BY t.task_due_date
                           """, (employee_id,))
            tasks = cursor.fetchall()

            # Статистика по задачам сотрудника
            total_employee_tasks = len(tasks)
            completed = sum(1 for t in tasks if t[3] == 'completed')
            in_progress = sum(1 for t in tasks if t[3] == 'in progress')
            pending = sum(1 for t in tasks if t[3] == 'pending')

            # Группируем задачи по проектам
            projects_dict = {}
            for task in tasks:
                proj_name = task[4]
                if proj_name not in projects_dict:
                    projects_dict[proj_name] = []
                projects_dict[proj_name].append(task)

            # Формируем отчёт
            report = f"""💼 ОТЧЁТ: ЗАГРУЗКА СОТРУДНИКА
{'=' * 70}

👤 ИНФОРМАЦИЯ:
ID: {employee_id}
Имя: {employee_name}
Должность: {employee_position}

{'=' * 70}
📊 СТАТИСТИКА СОТРУДНИКА:
{'=' * 70}
Всего задач: {total_employee_tasks}
  ✓ Завершено: {completed} ({completed * 100 // total_employee_tasks if total_employee_tasks > 0 else 0}%)
  ⏳ В работе: {in_progress} ({in_progress * 100 // total_employee_tasks if total_employee_tasks > 0 else 0}%)
  ⏸ Ожидает: {pending} ({pending * 100 // total_employee_tasks if total_employee_tasks > 0 else 0}%)

{'=' * 70}
"""

            if tasks:
                report += f"📋 ЗАДАЧИ ПО ПРОЕКТАМ ({len(projects_dict)} проектов):\n"
                report += f"{'=' * 70}\n\n"

                for proj_name, proj_tasks in projects_dict.items():
                    client_name = proj_tasks[0][5]
                    report += f"🔹 Проект: {proj_name}\n"
                    report += f"   Клиент: {client_name}\n"
                    report += f"   Задач: {len(proj_tasks)}\n\n"

                    for task in proj_tasks:
                        task_id, desc, due_date, status, _, _ = task
                        status_icon = "✓" if status == "completed" else "⏳" if status == "in progress" else "⏸"
                        report += f"   {status_icon} #{task_id}: {desc}\n"
                        report += f"      Срок: {due_date} | Статус: {status}\n"
                    report += f"\n{'-' * 70}\n\n"
            else:
                report += "⚠️ Сотрудник пока не назначен ни на одну задачу\n"
                report += "\n💡 Назначьте задачи через двойной клик по задаче в основном окне\n"

            dialog = ReportDialog(f"💼 Отчёт: {employee_name}", report, self)
            dialog.exec()
            logger.info(f"Отчёт по сотруднику {employee_name} (ID: {employee_id})")

    def generate_pdf_simple(self):
        logger.info("Начало генерации PDF-отчета")
        try:
            report_gen = ReportGenerator(cursor)
            pdf_path = report_gen.generate_pdf_report_simple()
            logger.info(f"PDF-отчет успешно создан: {pdf_path}")

            reply = QMessageBox.question(
                self,
                "PDF создан",
                f"PDF-отчет успешно создан!\n\nОткрыть файл?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                logger.debug(f"Открытие PDF-файла: {pdf_path}")
                if platform.system() == "Windows":
                    os.startfile(pdf_path)
                    logger.debug("PDF открыт через os.startfile (Windows)")
                elif platform.system() == "Darwin":
                    subprocess.run(["open", pdf_path])
                    logger.debug("PDF открыт через команду open (macOS)")
            else:
                logger.debug("Пользователь отказался от открытия PDF")

        except Exception as e:
            logger.error(f"Ошибка генерации PDF: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка генерации PDF: {e}")


def main():
    logger.info("=" * 50)
    logger.info("Запуск приложения ProjectManager")
    logger.info("=" * 50)

    try:
        app = QApplication(sys.argv)
        logger.debug("QApplication создан")

        window = ProjectManagerApp()
        logger.debug("Главное окно создано")

        window.show()
        logger.info("Главное окно отображено")

        exit_code = app.exec()
        logger.info(f"Приложение завершено с кодом: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске приложения: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
