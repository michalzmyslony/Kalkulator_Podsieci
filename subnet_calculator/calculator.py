import math
import ipaddress

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHBoxLayout, QHeaderView, QGridLayout, QCheckBox
)
from PySide6.QtGui import QFont, QRegularExpressionValidator
from PySide6.QtCore import Qt, Signal, QRegularExpression

# Import funkcji pomocniczych
from .utils import validate_ip_address, shake_widget

# [VLSM] Importujemy moduł do VLSM
from .vlsm import (
    parse_vlsm_requirements,
    calculate_subnets_vlsm,
    subnets_to_table
)

class SubnetCalculator(QWidget):
    # Sygnały do łączenia z innymi widgetami (np. wizualizacja i historia)
    calculation_done = Signal(object, list)  # (oryginalna sieć, lista podsieci)
    calculation_history = Signal(list)       # lista wynikowych wierszy

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kalkulator Podsieci")
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 14px;")

        layout = QVBoxLayout()
        form_layout = QGridLayout()
        self.widgets = {}

        # ---- Rodzaj adresu (IPv4 / IPv6) ----
        lbl_addr_type = QLabel("Rodzaj adresu:")
        lbl_addr_type.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_addr_type.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_addr_type, 0, 0)

        addr_type_combo = QComboBox()
        addr_type_combo.addItems(["IPv4", "IPv6"])
        addr_type_combo.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        addr_type_combo.currentIndexChanged.connect(self.update_address_type_dependent_fields)
        form_layout.addWidget(addr_type_combo, 0, 1)
        self.widgets["Rodzaj adresu:"] = addr_type_combo

        # ---- Klasa sieci (tylko dla IPv4) ----
        lbl_class = QLabel("Wybierz klasę sieci:")
        lbl_class.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_class.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_class, 1, 0)

        class_combo = QComboBox()
        class_combo.addItems(["A", "B", "C", "CIDR"])
        class_combo.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        class_combo.currentIndexChanged.connect(self.update_ip_placeholder)
        form_layout.addWidget(class_combo, 1, 1)
        self.widgets["Wybierz klasę sieci:"] = class_combo

        # ---- Adres startowy ----
        lbl_start_ip = QLabel("Adres startowy:")
        lbl_start_ip.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_start_ip.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_start_ip, 2, 0)

        ip_line = QLineEdit()
        ip_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        ip_line.editingFinished.connect(lambda: self.advanced_validate_ip(ip_line))
        form_layout.addWidget(ip_line, 2, 1)
        self.widgets["Adres startowy:"] = ip_line

        # ---- Maska ----
        lbl_mask = QLabel("Maska:")
        lbl_mask.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_mask.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_mask, 3, 0)

        mask_combo = QComboBox()
        mask_combo.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addWidget(mask_combo, 3, 1)
        self.widgets["Maska:"] = mask_combo

        # ---- Liczba podsieci ----
        lbl_num_subnets = QLabel("Liczba podsieci:")
        lbl_num_subnets.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_num_subnets.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_num_subnets, 4, 0)

        num_subnets_line = QLineEdit()
        num_subnets_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addWidget(num_subnets_line, 4, 1)
        self.widgets["Liczba podsieci:"] = num_subnets_line

        # ---- Liczba hostów na podsieć ----
        lbl_hosts = QLabel("Liczba hostów na podsieć:")
        lbl_hosts.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_hosts.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(lbl_hosts, 5, 0)

        hosts_line = QLineEdit()
        hosts_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addWidget(hosts_line, 5, 1)
        self.widgets["Liczba hostów na podsieć:"] = hosts_line

        # [VLSM] Checkbox do przełączania trybu
        self.vlsm_checkbox = QCheckBox("Tryb VLSM (zmienne rozmiary podsieci)")
        self.vlsm_checkbox.setStyleSheet("background-color: #1E1E1E; color: white;")
        form_layout.addWidget(self.vlsm_checkbox, 6, 0, 1, 2)

        # [VLSM] Pole tekstowe na wymagania (np. 1x100,2x50)
        lbl_vlsm = QLabel("Wymagania VLSM (np. 1x100,2x50):")
        lbl_vlsm.setFont(QFont("Arial", 10))
        lbl_vlsm.setAlignment(Qt.AlignLeft)
        form_layout.addWidget(lbl_vlsm, 7, 0)

        self.vlsm_requirements_line = QLineEdit()
        self.vlsm_requirements_line.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
        form_layout.addWidget(self.vlsm_requirements_line, 7, 1)

        layout.addLayout(form_layout)

        # ---- Przyciski akcji (Oblicz, Reset) ----
        button_layout = QHBoxLayout()
        self.calc_button = QPushButton("Oblicz")
        self.calc_button.setStyleSheet("background-color: #3A3A3A; padding: 10px; font-weight: bold;")
        self.calc_button.clicked.connect(self.calculate_subnets)
        button_layout.addWidget(self.calc_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #3A3A3A; padding: 10px; font-weight: bold;")
        self.reset_button.clicked.connect(self.reset_fields)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)

        # ---- Tabela wyników ----
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(9)
        self.result_table.setHorizontalHeaderLabels([
            "Nazwa", "Wymagane hosty", "Dostępne hosty", "Niewykorzystane hosty",
            "Adres sieciowy", "Maska i Slash", "Użyteczny zakres",
            "Broadcast", "Wildcard"
        ])
        self.result_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.result_table.horizontalHeader().setFixedHeight(80)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setStyleSheet("background-color: #2E2E2E;")

        layout.addWidget(self.result_table)
        self.setLayout(layout)

        self.update_address_type_dependent_fields()

    def advanced_validate_ip(self, line_edit):
        addr_type = self.widgets["Rodzaj adresu:"].currentText()
        ip_str = line_edit.text().strip()
        if validate_ip_address(ip_str, "IPv4" if addr_type == "IPv4" else "IPv6"):
            line_edit.setStyleSheet("background-color: #2E2E2E; padding: 5px;")
            line_edit.setToolTip("")
        else:
            line_edit.setStyleSheet("background-color: #2E2E2E; padding: 5px; border: 2px solid red;")
            line_edit.setToolTip("Nieprawidłowy adres IP")
            shake_widget(line_edit)

    def update_address_type_dependent_fields(self):
        addr_type = self.widgets["Rodzaj adresu:"].currentText()
        if addr_type == "IPv6":
            self.widgets["Wybierz klasę sieci:"].setEnabled(False)
            self.widgets["Wybierz klasę sieci:"].setCurrentIndex(0)
            self.widgets["Adres startowy:"].setText("2001:db8::")
            self.widgets["Adres startowy:"].setPlaceholderText("Np. 2001:db8::")
            self.update_mask_options(self.widgets["Maska:"], "IPv6")
            self.widgets["Adres startowy:"].setValidator(None)
        else:
            self.widgets["Wybierz klasę sieci:"].setEnabled(True)
            self.update_ip_placeholder()
            self.update_mask_options(self.widgets["Maska:"], "IPv4")
            ipv4_regex = QRegularExpression(
                r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)$'
            )
            validator = QRegularExpressionValidator(ipv4_regex)
            self.widgets["Adres startowy:"].setValidator(validator)

    def update_mask_options(self, mask_combobox, addr_type):
        mask_combobox.clear()
        if addr_type == "IPv4":
            # Dla IPv4 generujemy maski od /8 do /30
            mask_options = [(f"/{i}", str(ipaddress.IPv4Network((0, i)).netmask)) for i in range(8, 31)]
        else:
            # Dla IPv6 przykładowo od /32 do /128
            mask_options = [(f"/{i}", "") for i in range(32, 129)]

        for prefix, mask in mask_options:
            if mask:
                mask_combobox.addItem(f"{prefix} ({mask})")
            else:
                mask_combobox.addItem(f"{prefix}")

    def update_ip_placeholder(self):
        class_type = self.widgets["Wybierz klasę sieci:"].currentText()
        ranges = {
            "A": "10.0.0.0 - 10.255.255.255",
            "B": "172.16.0.0 - 172.31.255.255",
            "C": "192.168.0.0 - 192.168.255.255",
            "CIDR": "Dowolny adres IPv4"
        }
        if class_type in ["A", "B", "C"]:
            first_ip = ranges[class_type].split(" - ")[0]
            self.widgets["Adres startowy:"].setText(first_ip)
            self.widgets["Adres startowy:"].setPlaceholderText(ranges[class_type])
        else:
            self.widgets["Adres startowy:"].setText("")
            self.widgets["Adres startowy:"].setPlaceholderText("Wprowadź dowolny adres IPv4")

    def calculate_subnets(self):
        """
        Główna metoda wywoływana po kliknięciu "Oblicz".
        Sprawdza, czy używamy VLSM, czy standardowego podziału.
        """
        try:
            start_ip = self.widgets["Adres startowy:"].text().strip()
            mask_text = self.widgets["Maska:"].currentText().split(" ")[0]  # np. "/24"
            subnet_prefix = int(mask_text.replace("/", ""))

            # Tworzymy obiekt "sieci głównej"
            network = ipaddress.ip_network(f"{start_ip}/{subnet_prefix}", strict=False)

            # --- Tryb VLSM ---
            if self.vlsm_checkbox.isChecked():
                vlsm_string = self.vlsm_requirements_line.text().strip()
                if not vlsm_string:
                    raise ValueError("W trybie VLSM podaj wymagania w formacie np. 1x100,2x50.")

                # 1) Parsujemy np. "1x100,2x50" -> [(100,1), (50,2)]
                vlsm_list = parse_vlsm_requirements(vlsm_string)

                # 2) Obliczamy podsieci: otrzymujemy listę krotek (ip_network, required_hosts)
                subnets_info = calculate_subnets_vlsm(network, vlsm_list)

                # 3) Generujemy wiersze do tabeli (uwzględnia "Wymagane hosty" i "Niewykorzystane hosty")
                table_rows = subnets_to_table(subnets_info, label_prefix="Sieć")
                self.display_results(table_rows)

                # 4) Do wizualizacji i historii wysyłamy:
                #    - wizualizacja potrzebuje listy obiektów ip_network
                subnets_for_visual = [info[0] for info in subnets_info]

                self.calculation_done.emit(network, subnets_for_visual)
                self.calculation_history.emit(table_rows)

            # --- Tryb standardowy (równe podsieci) ---
            else:
                num_subnets = int(self.widgets["Liczba podsieci:"].text())
                hosts_per_subnet = int(self.widgets["Liczba hostów na podsieć:"].text())

                available_hosts = (
                    network.num_addresses - 2
                    if (network.version == 4 and network.num_addresses > 2)
                    else network.num_addresses
                )

                if hosts_per_subnet > available_hosts:
                    QMessageBox.critical(self, "Błąd", "Liczba hostów przekracza dostępne w wybranej sieci.")
                    return

                required_bits = math.ceil(math.log2(hosts_per_subnet + (2 if network.version == 4 else 0)))
                max_bits = 32 if network.version == 4 else 128
                new_prefix = max_bits - required_bits

                if new_prefix <= network.prefixlen:
                    QMessageBox.critical(
                        self,
                        "Błąd",
                        "Nie można utworzyć mniejszych podsieci. Wybierz inną maskę lub zmniejsz liczbę hostów."
                    )
                    return

                subnets = list(network.subnets(new_prefix=new_prefix))[:num_subnets]

                # Aktualizujemy maskę w GUI (podgląd)
                if network.version == 4:
                    self.widgets["Maska:"].setCurrentText(
                        f"/{new_prefix} ({str(ipaddress.IPv4Network((0, new_prefix)).netmask)})"
                    )
                else:
                    self.widgets["Maska:"].setCurrentText(f"/{new_prefix}")

                # Budujemy wyniki do tabeli
                results = []
                for i, subnet in enumerate(subnets):
                    avail = (
                        subnet.num_addresses - 2
                        if (subnet.version == 4 and subnet.num_addresses > 2)
                        else subnet.num_addresses
                    )
                    unused = avail - hosts_per_subnet
                    hosts_list = list(subnet.hosts()) if avail > 0 else []
                    first_usable = hosts_list[0] if hosts_list else ""
                    last_usable = hosts_list[-1] if hosts_list else ""

                    results.append([
                        f"Sieć {i + 1}",
                        hosts_per_subnet,    # Wymagane hosty
                        avail,               # Dostępne hosty
                        unused,              # Niewykorzystane
                        str(subnet.network_address),
                        f"{subnet.netmask if subnet.version == 4 else ''} /{subnet.prefixlen}",
                        f"{first_usable} - {last_usable}",
                        str(subnet.broadcast_address) if subnet.version == 4 else "Brak",
                        str(subnet.hostmask) if subnet.version == 4 else "Brak"
                    ])

                self.display_results(results)
                self.calculation_done.emit(network, subnets)
                self.calculation_history.emit(results)

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nieprawidłowe dane wejściowe: {e}")

    def display_results(self, rows):
        """
        Wyświetla wynikowe wiersze (listy) w self.result_table.
        rows powinno być listą list, każda wewnętrzna lista = 1 wiersz.
        """
        self.result_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_value in enumerate(row_data):
                item = QTableWidgetItem(str(col_value))
                item.setTextAlignment(Qt.AlignCenter)
                self.result_table.setItem(row_idx, col_idx, item)

        self.result_table.resizeColumnsToContents()
        self.result_table.resizeRowsToContents()

    def reset_fields(self):
        self.widgets["Rodzaj adresu:"].setCurrentIndex(0)
        self.update_address_type_dependent_fields()
        self.widgets["Liczba podsieci:"].clear()
        self.widgets["Liczba hostów na podsieć:"].clear()

        # Resetujemy VLSM
        self.vlsm_checkbox.setChecked(False)
        self.vlsm_requirements_line.clear()

        self.result_table.setRowCount(0)
