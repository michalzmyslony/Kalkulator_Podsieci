import math
import ipaddress

def parse_vlsm_requirements(vlsm_string):
    """
    Zamienia tekst w stylu '1x100,2x50' na listę krotek (hosts, count).
    Przykład: '1x100,2x50' -> [(100, 1), (50, 2)].
    """
    parts = [part.strip() for part in vlsm_string.split(",")]
    result = []
    for p in parts:
        if "x" not in p:
            raise ValueError(f"Niepoprawny format: '{p}'. Użyj np. '1x100'.")
        count_str, hosts_str = p.split("x")
        count = int(count_str)
        hosts = int(hosts_str)
        if count < 1 or hosts < 1:
            raise ValueError("Liczby w formacie VLSM muszą być dodatnie (min. 1).")
        result.append((hosts, count))
    return result

def calculate_subnets_vlsm(network, vlsm_list):
    """
    Alokuje w sieci 'network' podsieci o różnych rozmiarach, na podstawie listy (hosts, count).
    Zwraca listę krotek: (ip_network, required_hosts).
    """
    if network.version == 4 and network.num_addresses > 2:
        available = network.num_addresses - 2
    else:
        available = network.num_addresses

    # Suma wymaganych hostów (dla IPv4 +2 na net i broadcast)
    required_sum = 0
    for (hosts_needed, count_subnets) in vlsm_list:
        required_sum += (hosts_needed + (2 if network.version == 4 else 0)) * count_subnets

    if required_sum > available:
        raise ValueError("Wymagane adresy przekraczają wielkość wybranej sieci.")

    # Sortujemy od największych do najmniejszych
    sorted_list = sorted(vlsm_list, key=lambda x: x[0], reverse=True)

    allocated_subnets = []
    current_base = network.network_address
    max_bits = 32 if network.version == 4 else 128

    for (hosts_needed, count_subnets) in sorted_list:
        for _ in range(count_subnets):
            required_bits = math.ceil(math.log2(hosts_needed + (2 if network.version == 4 else 0)))
            new_prefix = max_bits - required_bits

            if new_prefix < network.prefixlen:
                raise ValueError(
                    f"Nie można przydzielić podsieci dla {hosts_needed} hostów. "
                    f"Prefix /{new_prefix} wykracza poza /{network.prefixlen}."
                )

            subnetwork = ipaddress.ip_network(f"{current_base}/{new_prefix}", strict=False)

            # Czy mieści się w sieci głównej?
            if subnetwork.network_address < network.network_address or \
               subnetwork.broadcast_address > network.broadcast_address:
                raise ValueError(f"Podsieć {subnetwork} wykracza poza sieć główną {network}.")

            # ZAMIENIAMY na krotkę: (subnetwork, hosts_needed)
            allocated_subnets.append((subnetwork, hosts_needed))

            # Następny wolny adres = broadcast + 1
            new_base_int = int(subnetwork.broadcast_address) + 1
            current_base = ipaddress.ip_address(new_base_int)

    return allocated_subnets

def subnets_to_table(subnets, label_prefix="Sieć"):
    """
    Przyjmuje listę krotek (ip_network, required_hosts) i generuje wiersze do wyświetlenia w QTableWidget.
    """
    results = []
    for i, (subnet, required) in enumerate(subnets):
        # Dostępne hosty w tej podsieci
        if subnet.version == 4 and subnet.num_addresses > 2:
            avail = subnet.num_addresses - 2
        else:
            # IPv6 lub bardzo małe IPv4 (/31, /32)
            avail = subnet.num_addresses

        # Niewykorzystane = dostępne - wymagane
        unused = avail - required if avail >= required else 0

        hosts_list = list(subnet.hosts()) if avail > 0 else []
        first_usable = hosts_list[0] if hosts_list else ""
        last_usable = hosts_list[-1] if hosts_list else ""

        results.append([
            f"{label_prefix} {i + 1}",
            required,             # Wymagane hosty (z VLSM)
            avail,               # Dostępne hosty
            unused,              # Niewykorzystane hosty
            str(subnet.network_address),
            f"{subnet.netmask if subnet.version == 4 else ''} /{subnet.prefixlen}",
            f"{first_usable} - {last_usable}",
            str(subnet.broadcast_address) if subnet.version == 4 else "Brak",
            str(subnet.hostmask) if subnet.version == 4 else "Brak"
        ])
    return results
