import ipaddress

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# Import funkcji pomocniczych
from .utils import validate_ip_address, shake_widget

class SubnetChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sprawdzanie podsieci")
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")
        main_layout = QVBoxLayout()

        header = QLabel("Sprawdzanie, czy adresy należą do tej samej podsieci")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        self.networks_layout = QVBoxLayout()
        self.rows_container = QWidget()
        self.rows_container.setLayout(self.networks_layout)
        main_layout.addWidget(self.rows_container)

        self.network_rows = []
        self.add_network_row()
        self.add_network_row()

        buttons_layout = QHBoxLayout()
        add_row_button = QPushButton("Dodaj sieć")
        add_row_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        add_row_button.clicked.connect(self.add_network_row)
        buttons_layout.addWidget(add_row_button)

        check_button = QPushButton("Sprawdź podsieci")
        check_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        check_button.clicked.connect(self.check_subnets)
        buttons_layout.addWidget(check_button)

        reset_button = QPushButton("Reset")
        reset_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        reset_button.clicked.connect(self.reset_checker)
        buttons_layout.addWidget(reset_button)

        main_layout.addLayout(buttons_layout)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels([
            "Nazwa", "Adres sieciowy", "Maska i Slash",
            "Użyteczny zakres", "Broadcast", "Wildcard", "Dostępne hosty"
        ])
        self.result_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        # Ustawiamy tryb dopasowywania rozmiaru kolumn
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.result_table.setStyleSheet("background-color: #2E2E2E;")
        main_layout.addWidget(self.result_table)

        self.setLayout(main_layout)

    def add_network_row(self):
        row_layout = QHBoxLayout()

        addr_type_combo = QComboBox()
        addr_type_combo.addItems(["IPv4", "IPv6"])
        addr_type_combo.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        row_layout.addWidget(addr_type_combo)

        ip_input = QLineEdit()
        ip_input.setPlaceholderText("Adres IP")
        ip_input.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        ip_input.editingFinished.connect(lambda: self.advanced_validate_ip(ip_input, addr_type_combo.currentText()))
        row_layout.addWidget(ip_input)

        mask_combo = QComboBox()
        mask_combo.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        self.update_mask_options(mask_combo, "IPv4")
        row_layout.addWidget(mask_combo)

        # Zmiana wersji adresu -> zmiana dostępnych masek
        addr_type_combo.currentIndexChanged.connect(
            lambda: self.update_mask_options(mask_combo, addr_type_combo.currentText())
        )
        addr_type_combo.currentIndexChanged.connect(
            lambda: self.advanced_validate_ip(ip_input, addr_type_combo.currentText())
        )

        remove_button = QPushButton("Usuń")
        remove_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        row_layout.addWidget(remove_button)

        row_widget = QWidget()
        row_widget.setLayout(row_layout)
        remove_button.clicked.connect(lambda _, widget=row_widget: self.remove_network_row(widget))
        self.networks_layout.addWidget(row_widget)
        self.network_rows.append(row_widget)

    def remove_network_row(self, row_widget):
        self.networks_layout.removeWidget(row_widget)
        row_widget.deleteLater()
        if row_widget in self.network_rows:
            self.network_rows.remove(row_widget)

    def update_mask_options(self, mask_combobox, addr_type):
        mask_combobox.clear()
        if addr_type == "IPv4":
            mask_options = [(f"/{i}", str(ipaddress.IPv4Network((0, i)).netmask)) for i in range(8, 31)]
        else:
            mask_options = [(f"/{i}", "") for i in range(32, 129)]

        for prefix, mask in mask_options:
            if mask:
                mask_combobox.addItem(f"{prefix} ({mask})")
            else:
                mask_combobox.addItem(f"{prefix}")

    def advanced_validate_ip(self, line_edit, addr_type):
        ip_str = line_edit.text().strip()
        if validate_ip_address(ip_str, "IPv4" if addr_type == "IPv4" else "IPv6"):
            line_edit.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
            line_edit.setToolTip("")
        else:
            line_edit.setStyleSheet("background-color: #2E2E2E; padding: 5px; border: 2px solid red;")
            line_edit.setToolTip("Nieprawidłowy adres IP")
            shake_widget(line_edit)

    def check_subnets(self):
        """
        Metoda sprawdza, czy wprowadzone adresy/maski należą do tej samej sieci.
        Następnie wyświetla wyniki w tabeli.
        """
        try:
            networks = []
            for row_widget in self.network_rows:
                layout = row_widget.layout()
                addr_type_combo = layout.itemAt(0).widget()
                ip_input = layout.itemAt(1).widget()
                mask_combo = layout.itemAt(2).widget()

                addr_type = addr_type_combo.currentText()
                ip = ip_input.text().strip()
                if not ip:
                    raise ValueError("Adres IPvX nie może być pusty.")

                prefix_text = mask_combo.currentText().split(" ")[0]  # np. "/24"
                prefix = int(prefix_text.replace("/", ""))

                network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
                networks.append(network)

            # Czy wszystkie sieci są takie same?
            unique_networks = list({net: None for net in networks}.keys())  # Unikalne obiekty sieci
            results = []

            if len(unique_networks) == 1:
                # Wszystkie te same sieci
                common_network = unique_networks[0]
                hosts_list = list(common_network.hosts()) if common_network.num_addresses > 2 else []
                row = [
                    "Wspólna sieć",
                    str(common_network.network_address),
                    f"{common_network.netmask if common_network.version == 4 else ''} /{common_network.prefixlen}",
                    f"{hosts_list[0]} - {hosts_list[-1]}" if hosts_list else "",
                    str(common_network.broadcast_address) if common_network.version == 4 else "Brak",
                    str(common_network.hostmask) if common_network.version == 4 else "Brak",
                    (common_network.num_addresses - 2)
                    if (common_network.version == 4 and common_network.num_addresses > 2)
                    else common_network.num_addresses
                ]
                results.append(row)
            else:
                # Różne sieci -> pokazujemy każdą z osobna
                for idx, net in enumerate(unique_networks):
                    hosts_list = list(net.hosts()) if net.num_addresses > 2 else []
                    row = [
                        f"Sieć {idx + 1}",
                        str(net.network_address),
                        f"{net.netmask if net.version == 4 else ''} /{net.prefixlen}",
                        f"{hosts_list[0]} - {hosts_list[-1]}" if hosts_list else "",
                        str(net.broadcast_address) if net.version == 4 else "Brak",
                        str(net.hostmask) if net.version == 4 else "Brak",
                        (net.num_addresses - 2)
                        if (net.version == 4 and net.num_addresses > 2)
                        else net.num_addresses
                    ]
                    results.append(row)

            self.display_results(results)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nieprawidłowe dane wejściowe: {e}")

    def display_results(self, results):
        self.result_table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value))
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(row_idx, col_idx, item)
        self.result_table.resizeColumnsToContents()
        self.result_table.resizeRowsToContents()

    def reset_checker(self):
        for row_widget in self.network_rows:
            self.networks_layout.removeWidget(row_widget)
            row_widget.deleteLater()
        self.network_rows = []
        self.add_network_row()
        self.add_network_row()
        self.result_table.setRowCount(0)
