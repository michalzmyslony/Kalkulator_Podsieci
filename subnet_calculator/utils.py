import ipaddress
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint

def validate_ip_address(ip_str, version="IPv4"):
    """
    Funkcja sprawdza poprawność adresu IP w zadanej wersji (IPv4/IPv6).
    """
    try:
        if version == "IPv4":
            ipaddress.IPv4Address(ip_str)
        else:
            ipaddress.IPv6Address(ip_str)
        return True
    except Exception:
        return False

def shake_widget(widget):
    """
    Prosta animacja trzęsienia się widgetu (np. gdy podano zły adres).
    """
    animation = QPropertyAnimation(widget, b"pos")
    orig_pos = widget.pos()
    animation.setDuration(300)
    animation.setKeyValueAt(0, orig_pos)
    animation.setKeyValueAt(0.25, orig_pos + QPoint(-10, 0))
    animation.setKeyValueAt(0.5, orig_pos + QPoint(10, 0))
    animation.setKeyValueAt(0.75, orig_pos + QPoint(-10, 0))
    animation.setKeyValueAt(1, orig_pos)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.start()
    widget.animation = animation  # Zachowujemy referencję
