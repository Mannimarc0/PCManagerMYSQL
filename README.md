# Система управления проектами

Программный комплекс для автоматизации работы руководителя проектов с возможностью учета клиентов, сотрудников, проектов и задач.

## Системные требования

- Python 3.13 или выше
- MySQL Server 8.0 или выше
- Windows / Linux / macOS

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd COURSACH
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных

Создайте базу данных MySQL:

```sql
CREATE DATABASE course_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Создайте таблицы:

```sql
USE course_db;

CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    client_name VARCHAR(90) NOT NULL,
    client_contact VARCHAR(90) NOT NULL UNIQUE
);

CREATE TABLE employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(90) NOT NULL UNIQUE,
    employee_position VARCHAR(90) NOT NULL
);

CREATE TABLE project (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_name VARCHAR(90) NOT NULL,
    project_client INT NOT NULL,
    project_start_date DATE NOT NULL,
    project_end_date DATE NOT NULL,
    FOREIGN KEY (project_client) REFERENCES clients(client_id) ON DELETE CASCADE
);

CREATE TABLE task (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    task_description VARCHAR(150) NOT NULL,
    task_project INT NOT NULL,
    task_due_date DATE NOT NULL,
    task_status VARCHAR(50) DEFAULT 'pending',
    task_employee INT,
    FOREIGN KEY (task_project) REFERENCES project(project_id) ON DELETE CASCADE,
    FOREIGN KEY (task_employee) REFERENCES employee(employee_id) ON DELETE SET NULL
);
```

### 4. Настройка подключения к БД

Откройте файл `course.py` и при необходимости измените параметры подключения:

```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",  # Измените на ваш пароль
    database="course_db",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
)
```

## Запуск программы

```bash
python course.py
```



```
PySide6>=6.6.0              # Qt6 для GUI
mysql-connector-python>=8.0 # MySQL драйвер
reportlab>=4.0.0            # Генерация PDF
pandas>=2.0.0               # Работа с Excel
openpyxl>=3.1.0             # Чтение/запись XLSX
email-validator>=2.0.0      # Валидация email
```

## Функциональные возможности

### Управление клиентами
- Добавление, редактирование, удаление клиентов
- Валидация email с проверкой уникальности
- Просмотр проектов клиента

### Управление сотрудниками
- Добавление, редактирование, удаление сотрудников
- Проверка уникальности ФИО
- Просмотр задач сотрудника

### Управление проектами
- Создание проектов с привязкой к клиенту
- Контроль сроков начала и окончания
- Просмотр задач проекта

### Управление задачами
- Создание задач с привязкой к проекту
- Назначение исполнителей
- 4 статуса: in progress, completed, pending, cancelled
- Быстрое редактирование по двойному клику на колонку

### Отчетность
- Простой PDF-отчет со всеми данными
- Специализированные отчеты (по клиентам, сотрудникам, проектам)
- Экспорт всех данных в Excel
- Импорт данных из Excel


## Ограничения полей

- Имя клиента: до 90 символов, только буквы, пробелы, дефисы
- Email: до 90 символов, формат email, уникальный
- ФИО сотрудника: до 90 символов, уникальное
- Должность: до 90 символов
- Название проекта: до 90 символов
- Описание задачи: до 150 символов, минимум 5 символов

## Логирование

Все операции записываются в файл `project_manager.log` с уровнями:
- DEBUG: детальная информация для отладки
- INFO: общая информация о работе программы
- WARNING: предупреждения
- ERROR: ошибки выполнения

## Troubleshooting

### Ошибка подключения к БД
- Проверьте, что MySQL Server запущен
- Убедитесь в правильности учетных данных (host, user, password)
- Проверьте существование базы данных `course_db`

### Ошибка создания PDF
- Убедитесь, что файл `timesnewromanpsmt.ttf` находится в корневой папке
- Проверьте права на запись в папку `reports/`
- Закройте открытые PDF-файлы

### Ошибка импорта Excel
- Проверьте наличие листов: Клиенты, Сотрудники, Проекты, Задачи
- Убедитесь в корректности заголовков колонок
- Закройте Excel-файл перед импортом

## Лицензия

Курсовая работа. Все права защищены.

## Автор

Разработано в рамках курсовой работы по дисциплине "ООП".
