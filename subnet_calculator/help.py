from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pomoc i dokumentacja")
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        layout = QVBoxLayout()

        header = QLabel("Pomoc i dokumentacja")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        help_text = (
            "<h2>Kalkulator Podsieci</h2>"
            "<p>Moduł pozwala na obliczanie podsieci zarówno dla adresów <strong>IPv4</strong> jak i "
            "<strong>IPv6</strong>. Dla IPv4 dostępne są klasy A, B, C i tryb <em>CIDR</em>. Możesz także "
            "wybrać maskę w formie slash (np. /24) lub jako maskę dziesiętną (np. 255.255.255.0). "
            "Wprowadź liczbę podsieci i liczbę hostów na podsieć – narzędzie obliczy odpowiednie adresy "
            "sieciowe, broadcast, użyteczny zakres hostów itp.</p>"
            "<p><strong>Tryb VLSM (zmienne rozmiary podsieci)</strong>: "
            "po zaznaczeniu odpowiedniej opcji możesz określić różne wymagania co do liczby hostów "
            "w poszczególnych podsieciach (np. 1x100,2x50). Kalkulator przydzieli je w przestrzeni adresowej "
            "zgodnie z metodą VLSM, tworząc podsieci o różnych wielkościach.</p>"

            "<h2>Sprawdzanie podsieci</h2>"
            "<p>W tym module możesz wprowadzić wiele wierszy z adresami (IPv4/IPv6) i ich maskami, aby "
            "sprawdzić, czy należą do tej samej podsieci. Program wyświetli adres sieciowy, maskę, zakres "
            "użytecznych hostów, broadcast (w przypadku IPv4) oraz hostmask (odwrotna maska) dla każdej "
            "z podanych sieci. Jeśli wszystkie adresy okażą się jednakowe w sensie prefixu, zobaczysz jedną "
            "wspólną sieć, w przeciwnym razie — kilka różnych.</p>"

            "<h2>Wizualizacja</h2>"
            "<p>Zakładka, która prezentuje <strong>drzewo</strong> z wygenerowanych podsieci. "
            "Po obliczeniach w Kalkulatorze Podsieci zobaczysz główny blok adresowy oraz poszczególne "
            "podsieci, z informacją o dostępnych hostach czy prefiksie. Możesz rozwinąć gałęzie, żeby "
            "przyjrzeć się szczegółom.</p>"

            "<h2>Generator planów</h2>"
            "<p>W tej zakładce wygenerujesz <strong>losowe scenariusze adresacji</strong>. "
            "Podajesz sieć bazową (np. 10.0.0.0/8), liczbę podsieci do wygenerowania i maksymalną liczbę "
            "hostów w jednej podsieci. Program automatycznie tworzy zapotrzebowania (np. 1x100,1x50...) "
            "i przydziela je metodą VLSM w wybranej przestrzeni. Dzięki temu szybko przetestujesz "
            "np. różne konfiguracje lub zobaczysz, jak dzieli się duże sieci na wiele podsieci o różnych rozmiarach.</p>"

            "<h2>Historia</h2>"
            "<p>Po każdym obliczeniu w <strong>Kalkulatorze Podsieci</strong> wyniki są zapisywane w "
            "zakładce <strong>Historia</strong>. Możesz tu przeglądać wszystkie dotychczasowe obliczenia, "
            "wraz z liczbą wymaganych i dostępnych hostów, adresami sieciowymi, maskami i innymi danymi. "
            "W przyszłości możesz rozbudować aplikację o funkcje <em>eksportu</em> (np. do pliku CSV, JSON) "
            "lub <em>importu</em> (wczytywanie poprzednio zapisanych wyników) — w zależności od potrzeb.</p>"

            "<h2>Pomoc</h2>"
            "<p>Aktualnie wyświetlana zakładka, w której znajdziesz informacje o poszczególnych modułach "
            "i sposobach korzystania z nich. Możesz ją rozszerzać o bardziej szczegółowe przykłady, "
            "zrzuty ekranu czy linki do dokumentacji sieciowej. W razie wątpliwości zapoznaj się z "
            "<em>Kalkulatorem Podsieci</em> lub wypróbuj poszczególne funkcje w praktyce.</p>"
        )

        help_view = QTextEdit()
        help_view.setReadOnly(True)
        help_view.setHtml(help_text)
        help_view.setStyleSheet("background-color: #2E2E2E;")
        layout.addWidget(help_view)

        self.setLayout(layout)
