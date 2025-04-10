import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget

# Import poszczególnych modułów:
from subnet_calculator.calculator import SubnetCalculator
from subnet_calculator.checker import SubnetChecker
from subnet_calculator.visualization import VisualizationWidget
from subnet_calculator.plan_generator import PlanGeneratorWidget
#from subnet_calculator.history import HistoryWidget
#from subnet_calculator.help import HelpWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalkulator Podsieci i Analiza Sieci")

        # Ustawiamy początkowy rozmiar okna
        self.setGeometry(200, 200, 1200, 850)
        # Jeśli chcesz wymusić, by nie dało się zmniejszyć poniżej pewnego rozmiaruls :
        # self.setMinimumSize(1200, 850)

        # Główny layout
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tworzymy poszczególne zakładki
        self.calculator_tab = SubnetCalculator()
        self.checker_tab = SubnetChecker()
        self.visualization_tab = VisualizationWidget()
        self.history_tab = HistoryWidget()

        self.plan_generator_tab = PlanGeneratorWidget()
        self.help_tab = HelpWidget()

        # Dodajemy zakładki w żądanej kolejności
        self.tabs.addTab(self.calculator_tab, "Kalkulator Podsieci")
        self.tabs.addTab(self.checker_tab, "Sprawdzanie podsieci")
        self.tabs.addTab(self.visualization_tab, "Wizualizacja")
        self.tabs.addTab(self.plan_generator_tab, "Generator planów")
        self.tabs.addTab(self.history_tab, "Historia")
        self.tabs.addTab(self.help_tab, "Pomoc")

        # Łączenie sygnałów kalkulatora z wizualizacją i historią
        self.calculator_tab.calculation_done.connect(self.visualization_tab.update_tree)
        self.calculator_tab.calculation_history.connect(self.history_tab.add_history_entries)

        # Ustawiamy layout
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
