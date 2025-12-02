from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self, cursor, output_dir="reports"):
        self.cursor = cursor
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Регистрация кириллического шрифта
        font_path = r'timesnewromanpsmt.ttf'
        self.font_name = 'Times'
        
        try:
            pdfmetrics.registerFont(TTFont(self.font_name, font_path))
            print(f"✓ Шрифт {self.font_name} зарегистрирован успешно")
        except Exception as e:
            print(f"✗ Ошибка регистрации {self.font_name}: {e}")
            raise
    def generate_pdf_report_simple(self, template_name="simple_report", output_filename="report.pdf"):
        filepath = os.path.join(self.output_dir, output_filename)
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.font_name
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=12,
            fontName=self.font_name
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=10
        )
        story.append(Paragraph("Отчет по управлению проектами", title_style))
        story.append(Paragraph(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Клиенты", heading_style))
        self.cursor.execute("SELECT * FROM clients")
        clients = self.cursor.fetchall()
        if clients:
            data = [['ID', 'Имя', 'Контакт']]
            for client in clients:
                data.append([str(client[0]), str(client[1]), str(client[2])])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Нет данных о клиентах", normal_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Проекты", heading_style))
        self.cursor.execute("""
            SELECT p.project_id, p.project_name, c.client_name, p.project_start_date, p.project_end_date
            FROM project p
            LEFT JOIN clients c ON p.project_client = c.client_id
        """)
        projects = self.cursor.fetchall()
        if projects:
            data = [['ID', 'Название', 'Клиент', 'Начало', 'Окончание']]
            for project in projects:
                data.append([
                    str(project[0]),
                    str(project[1]),
                    str(project[2]) if project[2] else "—",
                    str(project[3]),
                    str(project[4])
                ])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Нет данных о проектах", normal_style))
        story.append(PageBreak())
        
        # Таблица сотрудников
        story.append(Paragraph("Сотрудники", heading_style))
        self.cursor.execute("SELECT * FROM employee")
        employees = self.cursor.fetchall()
        if employees:
            data = [['ID', 'Имя', 'Должность']]
            for emp in employees:
                data.append([str(emp[0]), str(emp[1]), str(emp[2])])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Нет данных о сотрудниках", normal_style))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Таблица задач с исполнителями
        story.append(Paragraph("Задачи с назначенными исполнителями", heading_style))
        self.cursor.execute("""
            SELECT t.task_id, t.task_description, p.project_name, t.task_due_date, 
                   t.task_status, COALESCE(e.employee_name, 'Не назначен') as employee_name
            FROM task t
            LEFT JOIN project p ON t.task_project = p.project_id
            LEFT JOIN employee e ON t.task_assigned_employee = e.employee_id
        """)
        tasks = self.cursor.fetchall()
        if tasks:
            data = [['ID', 'Описание', 'Проект', 'Срок', 'Статус', 'Исполнитель']]
            for task in tasks:
                data.append([
                    str(task[0]),
                    str(task[1])[:30] + "..." if len(str(task[1])) > 30 else str(task[1]),
                    str(task[2])[:22] + "..." if task[2] and len(str(task[2])) > 22 else (str(task[2]) if task[2] else "—"),
                    str(task[3]),
                    str(task[4]),
                    str(task[5])[:22] + "..." if len(str(task[5])) > 22 else str(task[5])
                ])
            table = Table(data, colWidths=[0.4*inch, 1.6*inch, 1.3*inch, 0.9*inch, 0.9*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(table)
        else:
            story.append(Paragraph("Нет данных о задачах", normal_style))
        
        doc.build(story)
        return filepath