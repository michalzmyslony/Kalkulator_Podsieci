from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class VisualizationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Wizualizacja sieci")
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        layout = QVBoxLayout()

        header = QLabel("Wizualizacja sieci")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Element", "Szczegóły"])
        self.tree.header().setStyleSheet("background-color: #2E2E2E; color: white;")
        self.tree.setStyleSheet("background-color: #2E2E2E;")
        layout.addWidget(self.tree)

        refresh_button = QPushButton("Odśwież")
        refresh_button.setStyleSheet("background-color: #3A3A3A; padding: 5px;")
        refresh_button.clicked.connect(self.clear_tree)
        layout.addWidget(refresh_button)

        self.setLayout(layout)

    def update_tree(self, original_network, subnets):
        """
        Aktualizuje drzewo wizualizacji na podstawie sieci głównej i podsieci.
        """
        self.tree.clear()
        root_text = f"Sieć główna: {original_network.network_address} / {original_network.prefixlen}"
        root_item = QTreeWidgetItem([root_text, f"Liczba adresów: {original_network.num_addresses}"])
        self.tree.addTopLevelItem(root_item)

        for idx, subnet in enumerate(subnets):
            hosts_list = list(subnet.hosts()) if subnet.num_addresses > 2 else []
            details = f"Hosty: {hosts_list[0]} - {hosts_list[-1]}" if hosts_list else ""
            child_text = f"Podsieć {idx + 1}: {subnet.network_address} / {subnet.prefixlen}"
            child_item = QTreeWidgetItem([child_text, details])
            root_item.addChild(child_item)

        self.tree.expandAll()

    def clear_tree(self):
        self.tree.clear()
