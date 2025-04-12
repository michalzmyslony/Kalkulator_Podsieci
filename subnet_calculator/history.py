from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []  # lista wierszy historii
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Historia obliczeń")
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        layout = QVBoxLayout()

        header = QLabel("Historia obliczeń")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Nazwa", "Wymagane hosty", "Dostępne hosty", "Niewykorzystane hosty",
            "Adres sieciowy", "Maska i Slash", "Użyteczny zakres",
            "Broadcast", "Wildcard"
        ])
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        # Ustawiamy tryb dopasowywania rozmiaru kolumn
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table.setStyleSheet("background-color: #2E2E2E;")
        layout.addWidget(self.table)

        clear_button = QPushButton("Wyczyść historię")
        clear_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        clear_button.clicked.connect(self.clear_history)
        layout.addWidget(clear_button)

        self.setLayout(layout)

    def add_history_entries(self, rows):
        """
        Dodaje nowe wpisy (lista list) do historii i odświeża widok.
        """
        self.history.extend(rows)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.history))
        for row_idx, row_data in enumerate(self.history):
            for col_idx, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def clear_history(self):
        self.history = []
        self.table.setRowCount(0)
