import sys
import os
import math
import xml.etree.ElementTree as ET

# Parâmetros da zona UTM 23S
A_WGS84 = 6378137.0  # Semi-eixo maior WGS84
F_WGS84 = 1.0 / 298.257223563  # Achatamento
K0 = 0.9996
LON0_DEG = -45.0  # Longitude central da zona 23S


class Node:
    def __init__(self, id_original: int, lat: float, lon: float, id_interno: int):
        self.id_original = id_original
        self.lat = lat
        self.lon = lon
        self.x = 0.0
        self.y = 0.0
        self.id_interno = id_interno


class Way:
    def __init__(self):
        self.node_ids = []  # Armazena os IDs internos dos nós pertencentes à via


def converter_para_utm(lat_deg: float, lon_deg: float) -> tuple:
    """Converte coordenadas geográficas (Lat/Lon) para coordenadas planas UTM (Zona 23S)."""
    e2 = F_WGS84 * (2 - F_WGS84)  # Excentricidade ao quadrado
    ep2 = e2 / (1 - e2)  # Excentricidade secundária ao quadrado

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    lon0 = math.radians(LON0_DEG)

    N = A_WGS84 / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    T = math.tan(lat) ** 2
    C = ep2 * (math.cos(lat) ** 2)
    A = (lon - lon0) * math.cos(lat)

    # Cálculo do arco meridional
    M = A_WGS84 * (
            (1 - e2 / 4 - 3 * (e2 ** 2) / 64 - 5 * (e2 ** 3) / 256) * lat
            - (3 * e2 / 8 + 3 * (e2 ** 2) / 32 + 45 * (e2 ** 3) / 1024) * math.sin(2 * lat)
            + (15 * (e2 ** 2) / 256 + 45 * (e2 ** 3) / 1024) * math.sin(4 * lat)
            - (35 * (e2 ** 3) / 3072) * math.sin(6 * lat)
    )

    # Coordenada leste (X)
    x = K0 * N * (
                A + (1 - T + C) * (A ** 3) / 6 + (5 - 18 * T + T ** 2 + 72 * C - 58 * ep2) * (A ** 5) / 120) + 500000.0

    # Coordenada norte (Y)
    y = K0 * (M + N * math.tan(lat) * ((A ** 2) / 2 + (5 - T + 9 * C + 4 * (C ** 2)) * (A ** 4) / 24 + (
                61 - 58 * T + T ** 2 + 600 * C - 330 * ep2) * (A ** 6) / 720))

    # Ajuste para o hemisfério sul
    if lat_deg < 0:
        y += 10000000.0

    return x, y


def reduzir_escala(pontos: list, redutor: float):
    """Normaliza o ponto inicial em zero e aplica o fator redutor de escala."""
    if not pontos:
        return
    min_x = min(p.x for p in pontos)
    min_y = min(p.y for p in pontos)

    for p in pontos:
        p.x = (p.x - min_x) / redutor
        p.y = (p.y - min_y) / redutor


def parse_osm(filename: str):
    # Tratamento de strings equivalente às funções Left e Substr do C
    base, _ = os.path.splitext(filename)
    arq_saida = base + ".poly"

    nodes = []
    id_map = {}  # Dicionário para busca rápida do índice interno via id_original (Substitui get_node_index)
    ways = []

    try:
        # Usar o ElementTree nativo do Python torna o tratamento do XML muito mais seguro do que buscar texto puro com strstr
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception as e:
        print(f"Erro ao abrir ou processar o arquivo: {e}")
        return

    # Processando Nós (<node>)
    total_nodes = 0
    for node_elem in root.findall('node'):
        if 'id' in node_elem.attrib and 'lat' in node_elem.attrib and 'lon' in node_elem.attrib:
            id_orig = int(node_elem.attrib['id'])
            lat = float(node_elem.attrib['lat'])
            lon = float(node_elem.attrib['lon'])

            node_obj = Node(id_orig, lat, lon, total_nodes)
            node_obj.x, node_obj.y = converter_para_utm(lat, lon)

            nodes.append(node_obj)
            id_map[id_orig] = total_nodes
            total_nodes += 1

    # Processando Caminhos (<way>)
    for way_elem in root.findall('way'):
        current_way = Way()
        for nd_elem in way_elem.findall('nd'):
            ref = int(nd_elem.attrib['ref'])
            if ref in id_map:
                current_way.node_ids.append(id_map[ref])

        if len(current_way.node_ids) > 1:
            ways.append(current_way)

    if not nodes:
        print("Nenhum vértice válido encontrado no arquivo OSM.")
        return

    # Redução de escala (Equivalente ao redutor 2 do código em C)
    reduzir_escala(nodes, 2.0)

    # Inversão vertical do eixo Y para renderização correta em coordenadas de tela (ex: Canvas, TImage, Pygame)
    max_y = max(p.y for p in nodes)
    for p in nodes:
        p.y = max_y - p.y

    # Geração do arquivo estruturado de saída (.poly)
    with open(arq_saida, 'w') as out:
        # Cabeçalho dos vértices
        out.write(f"{len(nodes)}\t2\t0\t1\n")
        for p in nodes:
            out.write(f"{p.id_interno}\t{p.x:.6f}\t{p.y:.6f}\n")

        # Conta o total de arestas geradas pelos segmentos de retas consecutivos
        num_id = sum(len(w.node_ids) - 1 for w in ways)
        out.write(f"{num_id}\t1\n")

        # Impressão das conexões
        num_id_contador = 0
        for w in ways:
            for j in range(len(w.node_ids) - 1):
                origem = w.node_ids[j]
                destino = w.node_ids[j + 1]
                out.write(f"{num_id_contador}\t{origem}\t{destino}\t0\n")
                num_id_contador += 1

        out.write("0\n")

    print(f'Arquivo "{arq_saida}" criado com sucesso.')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: python {sys.argv[0]} arquivo.osm")
        sys.exit(1)
    parse_osm(sys.argv[1])
