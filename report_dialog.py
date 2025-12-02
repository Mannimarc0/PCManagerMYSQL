# Диалоговое окно для отображения отчётов со скроллом

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, 
    QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt


class ReportDialog(QDialog):
    # Диалоговое окно для отображения отчётов с возможностью скролла
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel(f"<h2>{title}</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Текстовое поле с прокруткой (только для чтения)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(content)
        
        # Устанавливаем моноширинный шрифт для лучшего отображения
        font = self.text_edit.font()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.text_edit.setFont(font)
        
        layout.addWidget(self.text_edit)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        # Кнопка "Закрыть"
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumHeight(35)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def set_content(self, content):
        # Обновить содержимое отчёта
        self.text_edit.setPlainText(content)
