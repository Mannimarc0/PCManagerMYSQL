from email_validator import validate_email as email_validate, EmailNotValidError
import re


class ValidationError(Exception):
    # Базовый класс для всех ошибок валидации
    def __init__(self, message, field_name=None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message)

    def __str__(self):
        if self.field_name:
            return f"Ошибка в поле '{self.field_name}': {self.message}"
        return self.message


class EmptyFieldError(ValidationError):
    # Ошибка пустого поля

    def __init__(self, field_name):
        super().__init__("Поле не может быть пустым", field_name)


class InvalidDateError(ValidationError):
    # Ошибка некорректной даты

    def __init__(self, message, field_name=None):
        super().__init__(message, field_name)


class InvalidEmailError(ValidationError):
    # Ошибка некорректного email

    def __init__(self, email_value, details=None):
        message = f"Некорректный формат email: {email_value}"
        if details:
            message += f"\nДетали: {details}"
        super().__init__(message, "Email")


class DatabaseError(Exception):
    # Ошибка работы с базой данных

    def __init__(self, operation, details):
        self.operation = operation
        self.details = details
        super().__init__(f"Ошибка БД при операции '{operation}': {details}")


class Validator:
    @staticmethod
    def validate_email(email):
        # Сначала проверяем базовый паттерн email только с английскими буквами
        email_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            raise InvalidEmailError(
                email,
                "Email должен содержать только английские буквы, цифры и символы ._-@"
            )

        # Дополнительная проверка через библиотеку
        try:
            validated = email_validate(email, check_deliverability=False)
            return validated.normalized
        except EmailNotValidError as e:
            raise InvalidEmailError(email, str(e))

    @staticmethod
    def check_email_uniqueness(email, cursor, exclude_id=None):
        # Проверка уникальности email в базе данных
        try:
            if exclude_id:
                cursor.execute(
                    "SELECT client_id, client_name FROM clients WHERE client_contact = %s AND client_id != %s",
                    (email, exclude_id)
                )
            else:
                cursor.execute(
                    "SELECT client_id, client_name FROM clients WHERE client_contact = %s",
                    (email,)
                )

            result = cursor.fetchone()
            if result:
                client_id, client_name = result
                raise ValidationError(
                    f"Email '{email}' уже используется клиентом '{client_name}' (ID: {client_id})",
                    "Email"
                )
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError("проверка уникальности email", str(e))

    @staticmethod
    def check_employee_name_uniqueness(name, cursor, exclude_id=None):
        # Проверка уникальности имени сотрудника в базе данных
        try:
            if exclude_id:
                cursor.execute(
                    "SELECT employee_id, employee_position FROM employee WHERE employee_name = %s AND employee_id != %s",
                    (name, exclude_id)
                )
            else:
                cursor.execute(
                    "SELECT employee_id, employee_position FROM employee WHERE employee_name = %s",
                    (name,)
                )

            result = cursor.fetchone()
            if result:
                emp_id, position = result
                raise ValidationError(
                    f"Сотрудник с именем '{name}' уже существует (Должность: {position}, ID: {emp_id})",
                    "Имя сотрудника"
                )

            return True

        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError("проверка уникальности имени сотрудника", str(e))

    @staticmethod
    def validate_non_empty(value, field_name, max_length=90):
        # Проверка, что поле не пустое и не превышает максимальную длину
        if not value or not value.strip():
            raise EmptyFieldError(field_name)

        value = value.strip()
        if len(value) > max_length:
            raise ValidationError(
                f"Превышена максимальная длина ({len(value)}/{max_length} символов)",
                field_name
            )

        return value

    @staticmethod
    def validate_client_data(name, contact):
        name = Validator.validate_non_empty(name, "Имя клиента", max_length=90)

        # Проверка, что имя содержит хотя бы одну букву
        if not re.search(r'[A-Za-zА-Яа-яЁё]', name):
            raise ValidationError(
                "Имя должно содержать хотя бы одну букву",
                "Имя клиента"
            )

        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-]+$", name):
            raise ValidationError("Имя может содержать только буквы, пробелы и дефисы", "Имя клиента")

        contact = Validator.validate_non_empty(contact, "Контакт", max_length=90)
        contact = Validator.validate_email(contact)

        return name, contact

    @staticmethod
    def validate_employee_data(name, position):
        name = Validator.validate_non_empty(name, "Имя сотрудника", max_length=90)
        position = Validator.validate_non_empty(position, "Должность", max_length=90)

        # Проверка, что имя содержит хотя бы одну букву
        if not re.search(r'[A-Za-zА-Яа-яЁё]', name):
            raise ValidationError(
                "Имя должно содержать хотя бы одну букву",
                "Имя сотрудника"
            )

        # Проверка, что должность содержит хотя бы одну букву
        if not re.search(r'[A-Za-zА-Яа-яЁё]', position):
            raise ValidationError(
                "Должность должна содержать хотя бы одну букву",
                "Должность"
            )

        # Проверка, что имя содержит только буквы, пробелы и дефисы
        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-]+$", name):
            raise ValidationError("Имя может содержать только буквы, пробелы и дефисы", "Имя сотрудника")
        if not re.match(r"^[A-Za-zА-Яа-яЁё\s\-]+$", position):
            raise ValidationError("Должность может содержать только буквы, пробелы и дефисы", "Должность")

        # Проверка минимальной длины
        if len(name) < 2:
            raise ValidationError("Имя должно быть не короче 2 символов", "Имя сотрудника")

        if len(position) < 2:
            raise ValidationError("Должность должна быть не короче 2 символов", "Должность")

        return name, position

    @staticmethod
    def validate_project_data(name, start_date, end_date):
        # Валидация данных проекта
        from PySide6.QtCore import QDate
        name = Validator.validate_non_empty(name, "Название проекта", max_length=90)
        # Проверка, что название содержит хотя бы одну букву
        if not re.search(r'[A-Za-zА-Яа-яЁё]', name):
            raise ValidationError(
                "Название должно содержать хотя бы одну букву",
                "Название проекта"
            )
        # Проверка допустимых символов (буквы, цифры, пробелы, дефисы)
        if not re.match(r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$', name):
            raise ValidationError(
                "Название может содержать только буквы, цифры, пробелы и дефисы",
                "Название проекта"
            )
        if end_date <= start_date:
            raise InvalidDateError(
                f"Дата окончания ({end_date.toString('dd.MM.yyyy')}) "
                f"должна быть позже даты начала ({start_date.toString('dd.MM.yyyy')})",
                "Дата окончания"
            )
        return name, start_date, end_date

    @staticmethod
    def validate_task_data(description, due_date, project_id=None):
        # Валидация данных задачи с проверкой срока относительно проекта
        from PySide6.QtCore import QDate
        import mysql.connector

        description = Validator.validate_non_empty(description, "Описание задачи", max_length=150)

        # Проверка минимальной длины
        if len(description) < 5:
            raise ValidationError(
                "Описание должно содержать не менее 5 символов",
                "Описание задачи"
            )

        # Проверка, что описание содержит хотя бы одну букву
        if not re.search(r'[A-Za-zА-Яа-яЁё]', description):
            raise ValidationError(
                "Описание должно содержать хотя бы одну букву",
                "Описание задачи"
            )

        # Проверка допустимых символов
        if not re.match(r'^[A-Za-zА-Яа-яЁё0-9\s\-]+$', description):
            raise ValidationError(
                "Описание может содержать только буквы, цифры, пробелы и дефисы",
                "Описание задачи"
            )
        current_date = QDate.currentDate()

        # Проверяем, что срок выполнения не раньше текущей даты
        if due_date < current_date:
            raise InvalidDateError(
                f"Срок выполнения ({due_date.toString('dd.MM.yyyy')}) не может быть раньше "
                f"текущей даты ({current_date.toString('dd.MM.yyyy')})",
                "Срок выполнения"
            )

        if project_id is not None and project_id <= 0:
            raise ValidationError("Некорректный ID проекта", "ID проекта")

        # Проверяем, что срок задачи не позже окончания проекта
        if project_id is not None:
            try:
                from course import cursor  # Импортируем cursor из course.py
                cursor.execute(
                    "SELECT project_end_date FROM project WHERE project_id = %s",
                    (project_id,)
                )
                result = cursor.fetchone()

                if result:
                    project_end_date_str = str(result[0])
                    project_end_date = QDate.fromString(project_end_date_str, "yyyy-MM-dd")

                    if due_date > project_end_date:
                        raise InvalidDateError(
                            f"Срок задачи ({due_date.toString('dd.MM.yyyy')}) не может быть позже "
                            f"окончания проекта ({project_end_date.toString('dd.MM.yyyy')})",
                            "Срок выполнения"
                        )
            except mysql.connector.Error as e:
                pass

        return description, due_date
