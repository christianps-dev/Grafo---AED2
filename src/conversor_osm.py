import os
import math
import xml.etree.ElementTree as ET
from config import FATOR_ESCALA

A_WGS84 = 6378137.0
F_WGS84 = 1.0 / 298.257223563
K0 = 0.9996
LON0_DEG = -45.0

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
        self.node_ids = []
        self.is_oneway = False

def converter_para_utm(lat_deg: float, lon_deg: float) -> tuple:
    e2 = F_WGS84 * (2 - F_WGS84)
    ep2 = e2 / (1 - e2)

    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    lon0 = math.radians(LON0_DEG)

    N = A_WGS84 / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    T = math.tan(lat) ** 2
    C = ep2 * (math.cos(lat) ** 2)
    A = (lon - lon0) * math.cos(lat)

    M = A_WGS84 * (
            (1 - e2 / 4 - 3 * (e2 ** 2) / 64 - 5 * (e2 ** 3) / 256) * lat
            - (3 * e2 / 8 + 3 * (e2 ** 2) / 32 + 45 * (e2 ** 3) / 1024) * math.sin(2 * lat)
            + (15 * (e2 ** 2) / 256 + 45 * (e2 ** 3) / 1024) * math.sin(4 * lat)
            - (35 * (e2 ** 3) / 3072) * math.sin(6 * lat)
    )

    x = K0 * N * (
            A + (1 - T + C) * (A ** 3) / 6 + 
            (5 - 18 * T + T ** 2 + 72 * C - 58 * ep2) * (A ** 5) / 120
    ) + 500000.0

    y = K0 * (
            M + N * math.tan(lat) * ((A ** 2) / 2 + 
            (5 - T + 9 * C + 4 * (C ** 2)) * (A ** 4) / 24 + 
            (61 - 58 * T + T ** 2 + 600 * C - 330 * ep2) * (A ** 6) / 720)
    )

    if lat_deg < 0:
        y += 10000000.0

    return x, y

def reduzir_escala(pontos: list, redutor: float):
    if not pontos:
        return
        
    min_x = min(p.x for p in pontos)
    min_y = min(p.y for p in pontos)

    for p in pontos:
        p.x = (p.x - min_x) / redutor
        p.y = (p.y - min_y) / redutor

def parse_osm(filename: str) -> str:
    nome_base = os.path.splitext(os.path.basename(filename))[0]
    
    diretorio_saida = os.path.join("out")
    os.makedirs(diretorio_saida, exist_ok=True)
    arq_saida = os.path.join(diretorio_saida, f"{nome_base}.poly")

    all_nodes_temp = {}

    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except Exception:
        return ""

    for node_elem in root.findall('node'):
        if 'id' in node_elem.attrib and 'lat' in node_elem.attrib and 'lon' in node_elem.attrib:
            id_orig = int(node_elem.attrib['id'])
            lat = float(node_elem.attrib['lat'])
            lon = float(node_elem.attrib['lon'])
            all_nodes_temp[id_orig] = (lat, lon)

    tipos_vias_validas = {
        'motorway', 'trunk', 'primary', 'secondary', 'tertiary',
        'unclassified', 'residential', 'living_street', 'motorway_link',
        'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link'
    }

    ways = []
    nos_utilizados_ids = set()

    for way_elem in root.findall('way'):
        current_way = Way()
        is_reverse = False
        is_highway = False
        
        for tag in way_elem.findall('tag'):
            if tag.attrib.get('k') == 'highway' and tag.attrib.get('v') in tipos_vias_validas:
                is_highway = True
            
            if tag.attrib.get('k') == 'oneway':
                val = tag.attrib.get('v')
                if val in ('yes', 'true', '1'):
                    current_way.is_oneway = True
                elif val == '-1': 
                    current_way.is_oneway = True
                    is_reverse = True

        if not is_highway:
            continue

        for nd_elem in way_elem.findall('nd'):
            ref = int(nd_elem.attrib['ref'])
            if ref in all_nodes_temp:
                current_way.node_ids.append(ref)
                nos_utilizados_ids.add(ref)

        if is_reverse:
            current_way.node_ids.reverse()

        if len(current_way.node_ids) > 1:
            ways.append(current_way)

    nodes = []
    id_map = {}
    total_nodes = 0

    for orig_id in nos_utilizados_ids:
        lat, lon = all_nodes_temp[orig_id]
        node_obj = Node(orig_id, lat, lon, total_nodes)
        node_obj.x, node_obj.y = converter_para_utm(lat, lon)
        nodes.append(node_obj)
        id_map[orig_id] = total_nodes
        total_nodes += 1

    if not nodes:
        return ""

    reduzir_escala(nodes, FATOR_ESCALA)

    max_y = max(p.y for p in nodes)
    for p in nodes:
        p.y = max_y - p.y

    with open(arq_saida, 'w') as out:
        out.write(f"{len(nodes)}\t2\t0\t1\n")
        for p in nodes:
            out.write(f"{p.id_interno}\t{p.x:.6f}\t{p.y:.6f}\n")

        num_id = sum(len(w.node_ids) - 1 for w in ways)
        out.write(f"{num_id}\t1\n")

        num_id_contador = 0
        for w in ways:
            tipo_via = 1 if w.is_oneway else 2 
            for j in range(len(w.node_ids) - 1):
                origem_interna = id_map[w.node_ids[j]]
                destino_interno = id_map[w.node_ids[j + 1]]
                out.write(f"{num_id_contador}\t{origem_interna}\t{destino_interno}\t{tipo_via}\n") 
                num_id_contador += 1

        out.write("0\n")

    return arq_saida