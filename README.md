Michał Zmyślony - 95820
Krystian Obst - 95552

Raport z wykorzystanych funkcjonalności
Projekt: Kalkulator Podsieci i Analiza Sieci

1. Struktura projektu
Projekt został podzielony na logiczne moduły:

main.py – główny plik uruchamiający aplikację, budujący główne okno z zakładkami.

subnet_calculator/ – folder zawierający moduły:

calculator.py – kalkulator podsieci (IPv4/IPv6) + obsługa trybu VLSM.

checker.py – sprawdzanie, czy adresy należą do tej samej podsieci.

visualization.py – wizualizacja podsieci w postaci drzewa.

plan_generator.py – generator losowych planów adresacji oparty na przestrzeni sieciowej.

history.py – zarządzanie historią obliczeń.

help.py – pomoc i dokumentacja użytkownika.

2. Technologie i biblioteki
Python 3.10+

PySide6 – framework GUI (Qt dla Pythona).

Matplotlib (w usuniętym module Statystyki – opcjonalnie używany wcześniej).

ipaddress (standardowa biblioteka Pythona do operacji na adresach IPv4/IPv6).

math – obliczenia matematyczne (np. logarytm przy obliczeniach hostów).

random – generowanie losowych danych w module Generator Planów.

3. Funkcjonalności użytkowe
3.1 Kalkulator Podsieci
Obsługuje adresy IPv4 i IPv6.

Pozwala:

Wybrać rodzaj adresu (IPv4 lub IPv6).

Wybrać klasę sieci (A, B, C, CIDR) dla IPv4.

Wprowadzić adres początkowy i maskę sieci.

Określić liczbę podsieci i liczbę hostów na podsieć.

Automatyczne obliczanie:

Adresów sieciowych.

Maski.

Adresu rozgłoszeniowego (broadcast) dla IPv4.

Zakresu użytecznych adresów hostów.

Wildcard mask.

Obsługa trybu VLSM:

Użytkownik może wprowadzić wymagania typu „1x100,2x50,1x10”.

Aplikacja rozdziela przestrzeń adresową dynamicznie według zapotrzebowania.

3.2 Sprawdzanie Podsietci
Możliwość wprowadzenia wielu adresów IP + maski dla każdego.

Walidacja poprawności IP.

Obliczenie:

Adresu sieciowego.

Maski i prefixu.

Broadcast (dla IPv4).

Wildcard.

Użytecznego zakresu hostów.

Weryfikacja, czy wszystkie adresy należą do tej samej podsieci.

3.3 Wizualizacja
Przedstawia strukturę wygenerowanych podsieci w formie drzewa.

Korzeń – główna sieć, dzieci – podsieci.

Informacje o liczbie adresów i zakresie hostów.

Automatyczne rozwijanie wszystkich gałęzi po aktualizacji.

3.4 Generator Planów Adresacji
Wprowadzenie:

Sieci bazowej (np. 10.0.0.0/8).

Liczby podsieci do wygenerowania.

Maksymalnej liczby hostów na podsieć.

Program losowo generuje wymagania (w stylu 1x100, 2x50, 3x10).

Rozdziela przestrzeń adresową zgodnie z algorytmem VLSM.

3.5 Historia
Zapisywanie wyników z kalkulatora:

Nazwa podsieci.

Wymagane hosty.

Dostępne hosty.

Adresy sieciowe, maski, broadcast, zakres hostów itp.

Możliwość przeglądania historii w tabeli.

Funkcja „Wyczyść historię” – usuwanie wszystkich zapisów.

3.6 Pomoc
Rozbudowana zakładka dokumentacji.

Szczegółowy opis:

Działania kalkulatora podsieci.

Sprawdzania podsieci.

Wizualizacji.

Generowania planów.

Obsługi historii.

Wskazówki dla użytkownika dotyczące pracy z każdym modułem.

4. Dodatkowe funkcjonalności i usprawnienia GUI
Walidacja pól IP: dynamiczne podświetlanie błędnych adresów.

Animacje (np. „trzęsienie” przy błędnych danych w polach IP).

Czytelny ciemny motyw GUI (kolory: tło #1E1E1E, aktywne elementy #2E2E2E, przyciski #3A3A3A).

Automatyczne skalowanie tabel (resizeColumnsToContents()).

Wczytywanie automatycznych placeholderów dla IP w zależności od klasy sieci (np. 10.0.0.0 dla klasy A).

Sygnały Qt (Signal) pomiędzy zakładkami: np. automatyczne aktualizowanie Wizualizacji i Historii po obliczeniu.

5. Moduły/usunięte funkcje
Statystyki (Wykresy) – wcześniej istniał moduł do rysowania wykresów Bar / Pie / Line, ale został usunięty na życzenie, ponieważ funkcjonalność nie spełniała oczekiwań.

Obecnie aplikacja nie generuje żadnych wykresów ani nie posiada funkcji statystycznych.

6. Podsumowanie
Projekt realizuje kompleksową obsługę kalkulacji i analizy podsieci IP.
Zapewnia:

Obliczenia dla IPv4 i IPv6,

Zaawansowany podział VLSM,

Weryfikację wielu sieci,

Wizualne przedstawienie wyników,

Przechowywanie i przeglądanie historii,

Generowanie przykładowych scenariuszy adresacji.

Interfejs jest intuicyjny, nowoczesny (ciemny motyw), a struktura kodu modułowa i łatwa do rozbudowy w przyszłości.
