# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'course_manager.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateEdit, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QTabWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab_clients = QWidget()
        self.tab_clients.setObjectName(u"tab_clients")
        self.verticalLayout_clients = QVBoxLayout(self.tab_clients)
        self.verticalLayout_clients.setObjectName(u"verticalLayout_clients")
        self.formLayout_clients = QFormLayout()
        self.formLayout_clients.setObjectName(u"formLayout_clients")
        self.label_client_name = QLabel(self.tab_clients)
        self.label_client_name.setObjectName(u"label_client_name")

        self.formLayout_clients.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_client_name)

        self.line_client_name = QLineEdit(self.tab_clients)
        self.line_client_name.setObjectName(u"line_client_name")

        self.formLayout_clients.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_client_name)

        self.label_client_contact = QLabel(self.tab_clients)
        self.label_client_contact.setObjectName(u"label_client_contact")

        self.formLayout_clients.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_client_contact)

        self.line_client_contact = QLineEdit(self.tab_clients)
        self.line_client_contact.setObjectName(u"line_client_contact")

        self.formLayout_clients.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_client_contact)


        self.verticalLayout_clients.addLayout(self.formLayout_clients)

        self.btn_add_client = QPushButton(self.tab_clients)
        self.btn_add_client.setObjectName(u"btn_add_client")

        self.verticalLayout_clients.addWidget(self.btn_add_client)

        self.hboxLayout = QHBoxLayout()
        self.hboxLayout.setObjectName(u"hboxLayout")
        self.line_search_client = QLineEdit(self.tab_clients)
        self.line_search_client.setObjectName(u"line_search_client")

        self.hboxLayout.addWidget(self.line_search_client)

        self.btn_delete_client = QPushButton(self.tab_clients)
        self.btn_delete_client.setObjectName(u"btn_delete_client")

        self.hboxLayout.addWidget(self.btn_delete_client)


        self.verticalLayout_clients.addLayout(self.hboxLayout)

        self.table_clients = QTableWidget(self.tab_clients)
        self.table_clients.setObjectName(u"table_clients")
        self.table_clients.setColumnCount(3)

        self.verticalLayout_clients.addWidget(self.table_clients)

        self.tabWidget.addTab(self.tab_clients, "")
        self.tab_employees = QWidget()
        self.tab_employees.setObjectName(u"tab_employees")
        self.verticalLayout_employees = QVBoxLayout(self.tab_employees)
        self.verticalLayout_employees.setObjectName(u"verticalLayout_employees")
        self.formLayout_employees = QFormLayout()
        self.formLayout_employees.setObjectName(u"formLayout_employees")
        self.label_employee_name = QLabel(self.tab_employees)
        self.label_employee_name.setObjectName(u"label_employee_name")

        self.formLayout_employees.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_employee_name)

        self.line_employee_name = QLineEdit(self.tab_employees)
        self.line_employee_name.setObjectName(u"line_employee_name")

        self.formLayout_employees.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_employee_name)

        self.label_employee_position = QLabel(self.tab_employees)
        self.label_employee_position.setObjectName(u"label_employee_position")

        self.formLayout_employees.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_employee_position)

        self.line_employee_position = QLineEdit(self.tab_employees)
        self.line_employee_position.setObjectName(u"line_employee_position")

        self.formLayout_employees.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_employee_position)


        self.verticalLayout_employees.addLayout(self.formLayout_employees)

        self.btn_add_employee = QPushButton(self.tab_employees)
        self.btn_add_employee.setObjectName(u"btn_add_employee")

        self.verticalLayout_employees.addWidget(self.btn_add_employee)

        self.hboxLayout1 = QHBoxLayout()
        self.hboxLayout1.setObjectName(u"hboxLayout1")
        self.line_search_employee = QLineEdit(self.tab_employees)
        self.line_search_employee.setObjectName(u"line_search_employee")

        self.hboxLayout1.addWidget(self.line_search_employee)

        self.btn_delete_employee = QPushButton(self.tab_employees)
        self.btn_delete_employee.setObjectName(u"btn_delete_employee")

        self.hboxLayout1.addWidget(self.btn_delete_employee)


        self.verticalLayout_employees.addLayout(self.hboxLayout1)

        self.table_employees = QTableWidget(self.tab_employees)
        self.table_employees.setObjectName(u"table_employees")
        self.table_employees.setColumnCount(3)

        self.verticalLayout_employees.addWidget(self.table_employees)

        self.tabWidget.addTab(self.tab_employees, "")
        self.tab_projects = QWidget()
        self.tab_projects.setObjectName(u"tab_projects")
        self.verticalLayout_projects = QVBoxLayout(self.tab_projects)
        self.verticalLayout_projects.setObjectName(u"verticalLayout_projects")
        self.formLayout_projects = QFormLayout()
        self.formLayout_projects.setObjectName(u"formLayout_projects")
        self.label_project_name = QLabel(self.tab_projects)
        self.label_project_name.setObjectName(u"label_project_name")

        self.formLayout_projects.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_project_name)

        self.line_project_name = QLineEdit(self.tab_projects)
        self.line_project_name.setObjectName(u"line_project_name")

        self.formLayout_projects.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_project_name)

        self.label_project_start = QLabel(self.tab_projects)
        self.label_project_start.setObjectName(u"label_project_start")

        self.formLayout_projects.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_project_start)

        self.date_project_start = QDateEdit(self.tab_projects)
        self.date_project_start.setObjectName(u"date_project_start")
        self.date_project_start.setCalendarPopup(True)

        self.formLayout_projects.setWidget(1, QFormLayout.ItemRole.FieldRole, self.date_project_start)

        self.label_project_end = QLabel(self.tab_projects)
        self.label_project_end.setObjectName(u"label_project_end")

        self.formLayout_projects.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_project_end)

        self.date_project_end = QDateEdit(self.tab_projects)
        self.date_project_end.setObjectName(u"date_project_end")
        self.date_project_end.setCalendarPopup(True)

        self.formLayout_projects.setWidget(2, QFormLayout.ItemRole.FieldRole, self.date_project_end)


        self.verticalLayout_projects.addLayout(self.formLayout_projects)

        self.btn_add_project = QPushButton(self.tab_projects)
        self.btn_add_project.setObjectName(u"btn_add_project")

        self.verticalLayout_projects.addWidget(self.btn_add_project)

        self.hboxLayout2 = QHBoxLayout()
        self.hboxLayout2.setObjectName(u"hboxLayout2")
        self.line_search_project = QLineEdit(self.tab_projects)
        self.line_search_project.setObjectName(u"line_search_project")

        self.hboxLayout2.addWidget(self.line_search_project)

        self.btn_delete_project = QPushButton(self.tab_projects)
        self.btn_delete_project.setObjectName(u"btn_delete_project")

        self.hboxLayout2.addWidget(self.btn_delete_project)


        self.verticalLayout_projects.addLayout(self.hboxLayout2)

        self.table_projects = QTableWidget(self.tab_projects)
        self.table_projects.setObjectName(u"table_projects")
        self.table_projects.setColumnCount(5)

        self.verticalLayout_projects.addWidget(self.table_projects)

        self.tabWidget.addTab(self.tab_projects, "")
        self.tab_tasks = QWidget()
        self.tab_tasks.setObjectName(u"tab_tasks")
        self.verticalLayout_tasks = QVBoxLayout(self.tab_tasks)
        self.verticalLayout_tasks.setObjectName(u"verticalLayout_tasks")
        self.formLayout_tasks = QFormLayout()
        self.formLayout_tasks.setObjectName(u"formLayout_tasks")
        self.label_task_description = QLabel(self.tab_tasks)
        self.label_task_description.setObjectName(u"label_task_description")

        self.formLayout_tasks.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_task_description)

        self.line_task_description = QLineEdit(self.tab_tasks)
        self.line_task_description.setObjectName(u"line_task_description")

        self.formLayout_tasks.setWidget(0, QFormLayout.ItemRole.FieldRole, self.line_task_description)

        self.label_task_due = QLabel(self.tab_tasks)
        self.label_task_due.setObjectName(u"label_task_due")

        self.formLayout_tasks.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_task_due)

        self.date_task_due = QDateEdit(self.tab_tasks)
        self.date_task_due.setObjectName(u"date_task_due")
        self.date_task_due.setCalendarPopup(True)

        self.formLayout_tasks.setWidget(1, QFormLayout.ItemRole.FieldRole, self.date_task_due)


        self.verticalLayout_tasks.addLayout(self.formLayout_tasks)

        self.btn_add_task = QPushButton(self.tab_tasks)
        self.btn_add_task.setObjectName(u"btn_add_task")

        self.verticalLayout_tasks.addWidget(self.btn_add_task)

        self.hboxLayout3 = QHBoxLayout()
        self.hboxLayout3.setObjectName(u"hboxLayout3")
        self.line_search_task = QLineEdit(self.tab_tasks)
        self.line_search_task.setObjectName(u"line_search_task")

        self.hboxLayout3.addWidget(self.line_search_task)

        self.btn_delete_task = QPushButton(self.tab_tasks)
        self.btn_delete_task.setObjectName(u"btn_delete_task")

        self.hboxLayout3.addWidget(self.btn_delete_task)


        self.verticalLayout_tasks.addLayout(self.hboxLayout3)

        self.table_tasks = QTableWidget(self.tab_tasks)
        self.table_tasks.setObjectName(u"table_tasks")
        self.table_tasks.setColumnCount(6)

        self.verticalLayout_tasks.addWidget(self.table_tasks)

        self.tabWidget.addTab(self.tab_tasks, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.horizontalLayout_buttons = QHBoxLayout()
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.spacerItem)

        self.btn_import_excel = QPushButton(self.centralwidget)
        self.btn_import_excel.setObjectName(u"btn_import_excel")

        self.horizontalLayout_buttons.addWidget(self.btn_import_excel)

        self.btn_export_excel = QPushButton(self.centralwidget)
        self.btn_export_excel.setObjectName(u"btn_export_excel")

        self.horizontalLayout_buttons.addWidget(self.btn_export_excel)

        self.btn_generate_pdf_simple = QPushButton(self.centralwidget)
        self.btn_generate_pdf_simple.setObjectName(u"btn_generate_pdf_simple")

        self.horizontalLayout_buttons.addWidget(self.btn_generate_pdf_simple)


        self.verticalLayout.addLayout(self.horizontalLayout_buttons)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430\u043c\u0438", None))
        self.label_client_name.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f \u043a\u043b\u0438\u0435\u043d\u0442\u0430:", None))
        self.label_client_contact.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043d\u0442\u0430\u043a\u0442:", None))
        self.btn_add_client.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043a\u043b\u0438\u0435\u043d\u0442\u0430", None))
        self.line_search_client.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a \u043a\u043b\u0438\u0435\u043d\u0442\u0430...", None))
        self.btn_delete_client.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.table_clients.setHorizontalHeaderLabels([
            QCoreApplication.translate("MainWindow", u"ID", None),
            QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f", None),
            QCoreApplication.translate("MainWindow", u"\u041a\u043e\u043d\u0442\u0430\u043a\u0442", None)])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_clients), QCoreApplication.translate("MainWindow", u"\u041a\u043b\u0438\u0435\u043d\u0442\u044b", None))
        self.label_employee_name.setText(QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0430:", None))
        self.label_employee_position.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c:", None))
        self.btn_add_employee.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0430", None))
        self.line_search_employee.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a \u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0430...", None))
        self.btn_delete_employee.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.table_employees.setHorizontalHeaderLabels([
            QCoreApplication.translate("MainWindow", u"ID", None),
            QCoreApplication.translate("MainWindow", u"\u0418\u043c\u044f", None),
            QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c", None)])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_employees), QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438", None))
        self.label_project_name.setText(QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u0440\u043e\u0435\u043a\u0442\u0430:", None))
        self.label_project_start.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430 \u043d\u0430\u0447\u0430\u043b\u0430:", None))
        self.label_project_end.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0430\u0442\u0430 \u043e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u044f:", None))
        self.btn_add_project.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u0440\u043e\u0435\u043a\u0442", None))
        self.line_search_project.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a \u043f\u0440\u043e\u0435\u043a\u0442\u0430...", None))
        self.btn_delete_project.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.table_projects.setHorizontalHeaderLabels([
            QCoreApplication.translate("MainWindow", u"ID", None),
            QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435", None),
            QCoreApplication.translate("MainWindow", u"\u041a\u043b\u0438\u0435\u043d\u0442", None),
            QCoreApplication.translate("MainWindow", u"\u041d\u0430\u0447\u0430\u043b\u043e", None),
            QCoreApplication.translate("MainWindow", u"\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435", None)])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_projects), QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0435\u043a\u0442\u044b", None))
        self.label_task_description.setText(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u0437\u0430\u0434\u0430\u0447\u0438:", None))
        self.label_task_due.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0440\u043e\u043a \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f:", None))
        self.btn_add_task.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0437\u0430\u0434\u0430\u0447\u0443", None))
        self.line_search_task.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0438\u0441\u043a \u0437\u0430\u0434\u0430\u0447\u0438...", None))
        self.btn_delete_task.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c", None))
        self.table_tasks.setHorizontalHeaderLabels([
            QCoreApplication.translate("MainWindow", u"ID", None),
            QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435", None),
            QCoreApplication.translate("MainWindow", u"\u041f\u0440\u043e\u0435\u043a\u0442", None),
            QCoreApplication.translate("MainWindow", u"\u0421\u0440\u043e\u043a", None),
            QCoreApplication.translate("MainWindow", u"\u0421\u0442\u0430\u0442\u0443\u0441", None),
            QCoreApplication.translate("MainWindow", u"\u0418\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c", None)])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_tasks), QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0434\u0430\u0447\u0438", None))
        self.btn_import_excel.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0438\u0437 Excel", None))
        self.btn_export_excel.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0433\u0440\u0443\u0437\u0438\u0442\u044c \u0432 Excel", None))
        self.btn_generate_pdf_simple.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c PDF \u043e\u0442\u0447\u0435\u0442", None))
    # retranslateUi

