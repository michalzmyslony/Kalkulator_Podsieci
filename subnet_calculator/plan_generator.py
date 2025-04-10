import ipaddress
import random
import math

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QFormLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# Zakładamy, że masz już vlsm.py w tym samym folderze:
from .vlsm import parse_vlsm_requirements, calculate_subnets_vlsm, subnets_to_table
from .utils import shake_widget  # jeśli chcesz animację przy błędach


class PlanGeneratorWidget(QWidget):
    """
    Generator przykładowych planów adresacji (losowo).
    Pozwala wprowadzić:
      - Sieć bazową (np. 10.0.0.0/8)
      - Liczbę podsieci do wygenerowania
      - Maksymalną liczbę hostów w pojedynczej podsieci
    Następnie losowo tworzymy "wymagania VLSM" (np. 1x100,2x50),
    a w końcu wywołujemy calculate_subnets_vlsm, by uzyskać finalny podział.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Generator planów adresacji")
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")

        main_layout = QVBoxLayout(self)

        header = QLabel("Generator przykładowych planów adresacji")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Formularz parametrów
        form_layout = QFormLayout()

        self.network_line = QLineEdit()
        self.network_line.setPlaceholderText("Np. 10.0.0.0/8")
        self.network_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        self.network_line.setText("10.0.0.0/8")  # przykładowa domyślna
        form_layout.addRow("Sieć bazowa:", self.network_line)

        self.num_subnets_line = QLineEdit()
        self.num_subnets_line.setPlaceholderText("Liczba podsieci (np. 5)")
        self.num_subnets_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addRow("Liczba podsieci:", self.num_subnets_line)

        self.max_hosts_line = QLineEdit()
        self.max_hosts_line.setPlaceholderText("Maks hostów w podsieci (np. 200)")
        self.max_hosts_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addRow("Max hostów/podsieć:", self.max_hosts_line)

        main_layout.addLayout(form_layout)

        # Przycisk generuj
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generuj plan")
        self.generate_button.setStyleSheet("background-color: #3A3A3A; padding: 10px; font-weight: bold;")
        self.generate_button.clicked.connect(self.generate_plan)
        button_layout.addWidget(self.generate_button)

        main_layout.addLayout(button_layout)

        # Tabela wynikowa
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(9)
        self.result_table.setHorizontalHeaderLabels([
            "Nazwa", "Wymagane hosty", "Dostępne hosty", "Niewykorzystane hosty",
            "Adres sieciowy", "Maska i Slash", "Użyteczny zakres",
            "Broadcast", "Wildcard"
        ])
        self.result_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setStyleSheet("background-color: #2E2E2E;")

        main_layout.addWidget(self.result_table)

    def generate_plan(self):
        """
        Po kliknięciu "Generuj plan":
          1) Pobieramy sieć bazową (np. 10.0.0.0/8)
          2) Liczbę podsieci (n)
          3) Max hostów/podsieć
          4) Tworzymy w stringu np. "1x123,1x44,1x10" itp. -> parse_vlsm_requirements -> calculate_subnets_vlsm
        """
        try:
            base_network_str = self.network_line.text().strip()
            if not base_network_str:
                raise ValueError("Musisz podać sieć bazową (np. 10.0.0.0/8).")

            # Tworzymy obiekt sieci
            base_network = ipaddress.ip_network(base_network_str, strict=False)

            n_str = self.num_subnets_line.text().strip()
            if not n_str:
                raise ValueError("Podaj liczbę podsieci do wygenerowania.")
            n = int(n_str)
            if n < 1:
                raise ValueError("Liczba podsieci musi być >= 1.")

            max_str = self.max_hosts_line.text().strip()
            if not max_str:
                raise ValueError("Podaj maksymalną liczbę hostów.")
            max_hosts = int(max_str)
            if max_hosts < 1:
                raise ValueError("Maksymalna liczba hostów musi być >= 1.")

            # Generujemy losowe wartości hostów w zakresie [2 .. max_hosts]
            # (dlaczego 2? bo min. 2 hosty w klasycznym IPv4 - net i broadcast)
            # Można to oczywiście modyfikować wg własnych założeń
            generated_reqs = []
            for _ in range(n):
                random_hosts = random.randint(2, max_hosts)
                # Każdą wygenerowaną podsieć chcemy "1x[random_hosts]"
                generated_reqs.append(f"1x{random_hosts}")

            # np. ["1x103", "1x77", "1x4"] -> "1x103,1x77,1x4"
            vlsm_string = ",".join(generated_reqs)

            # Parsujemy i liczymy
            vlsm_list = parse_vlsm_requirements(vlsm_string)
            subnets_info = calculate_subnets_vlsm(base_network, vlsm_list)

            table_rows = subnets_to_table(subnets_info, label_prefix="Losowa podsieć")
            self.display_results(table_rows)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd podczas generowania planu: {e}")
            shake_widget(self)

    def display_results(self, rows):
        """
        Wyświetla przekazane wiersze (lista list) w QTableWidget.
        """
        self.result_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value))
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(row_idx, col_idx, item)
        self.result_table.resizeColumnsToContents()
        self.result_table.resizeRowsToContents()
