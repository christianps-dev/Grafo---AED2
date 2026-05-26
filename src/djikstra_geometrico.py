import math
from heap import Heap
from config import FATOR_ESCALA
import time
# SE PRONUNCIA DI Á IS TRA 

INF = 1e9

class Vertice:
    def __init__(self, v_id: int, x: float, y: float):
        self.id = v_id
        self.x = x
        self.y = y

class Aresta:
    def __init__(self, orig: int, dest: int, tipo: int):
        self.orig = orig
        self.dest = dest
        self.tipo = tipo # 1 = Mão única, 2 = mão dupla

def calc_dist(x0: float, y0: float, x1: float, y1: float) -> float:
    """Calcula a distância euclidiana entre dois pontos bidimensionais."""
    return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

def construir_grafo(vertices: list, arestas: list) -> list:
    total_vertices = len(vertices)
    lista_adj = [[] for _ in range(total_vertices)]
    
    for art in arestas:
        a = art.orig
        b = art.dest
        distancia = calc_dist(vertices[a].x, vertices[a].y, vertices[b].x, vertices[b].y)
        
        # O lado 'A -> B' sempre existe
        lista_adj[a].append((distancia, b))
        
        # O lado 'B -> A' SÓ existe se for mão dupla (tipo == 2)
        if art.tipo == 2:
            lista_adj[b].append((distancia, a))

    return lista_adj


def dijkstra(grafo: list, vertices: list, inicio: int, fim: int):
    total_vertices = len(vertices)
    dist = [INF] * total_vertices
    prev = [-1] * total_vertices

    dist[inicio] = 0.0

    minha_heap = Heap()
    minha_heap.insert((0.0, inicio))

    # --- (Estatísticas) ---
    nos_explorados = 0
    tempo_inicio = time.perf_counter() 

    while not minha_heap.isEmpty():
        dist_atual, u = minha_heap.extractMin()

        if dist_atual > dist[u]:
            continue
            
       
        nos_explorados += 1

        for peso, v in grafo[u]:
            if dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                prev[v] = u
                minha_heap.insert((dist[v], v))

    
    tempo_fim = time.perf_counter()
    tempo_processamento_ms = (tempo_fim - tempo_inicio) * 1000

    if dist[fim] == INF:
        print(f"Sem caminho entre {inicio} e {fim}")
        return None

   
    distancia_pixels = dist[fim]
    distancia_metros = distancia_pixels * FATOR_ESCALA

    
    caminho = []
    v = fim
    while v != -1:
        caminho.append(v)
        v = prev[v]
    caminho.reverse()

    
    print("\n" + "=" * 40)
    print(" ESTATÍSTICAS DA ROTA ".center(40, "="))
    print("=" * 40)
    print(f"Tempo de processamento: {tempo_processamento_ms:.2f} ms")
    print(f"Número de nós explorados: {nos_explorados}")
    print(f"Custo total (na tela): {distancia_pixels:.2f} pixels")
    print(f"Custo total (real): {distancia_metros:.2f} metros")
    print("=" * 40 + "\n")

    
    resultado = {
        "caminho_ids": caminho,
        "distancia_pixels": distancia_pixels,
        "distancia_metros": distancia_metros,
        "nos_explorados": nos_explorados,
        "tempo_ms": tempo_processamento_ms
    }
    
    return resultado

def carregar_mapa_poly(caminho_arquivo):
    vertices = []
    arestas = []
    
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()

    linha_v = linhas[0].split()
    total_vertices = int(linha_v[0])
    
    for i in range(1, total_vertices + 1):
        dados = linhas[i].split()
        id_vert = int(dados[0])
        x = float(dados[1])
        y = float(dados[2])
        vertices.append(Vertice(id_vert, x, y)) 
        
    linha_a = linhas[total_vertices + 1].split()
    total_arestas = int(linha_a[0])
    
    inicio_arestas = total_vertices + 2
    for i in range(inicio_arestas, inicio_arestas + total_arestas):
        dados = linhas[i].split()
        origem = int(dados[1])
        destino = int(dados[2])
        tipo = int(dados[3])  
        arestas.append(Aresta(origem, destino, tipo)) 
        
    return vertices, arestas

"""def main():
    print("Carregando mapa real...")
    vertices, arestas = carregar_mapa_poly("../out/mapaUFG.poly")
    
    
    grafo = construir_grafo(vertices, arestas)
    
    total_vertices = len(vertices)
    total_arestas = len(arestas)
    
    print("Menor caminho entre dois vertices - algoritmo de Dijkstra\n")    
    print(f"Total de vertices: {total_vertices}")
    print(f"Total de arestas : {total_arestas}")

    try:
        origem = int(input(f"Digite o vertice de origem (0 a {total_vertices - 1}): "))
        destino = int(input(f"Digite o vertice de destino (0 a {total_vertices - 1}): "))

        if 0 <= origem < total_vertices and 0 <= destino < total_vertices:
            dijkstra(grafo, vertices, origem, destino)
        else:
            print("Indices invalidos.")
    except ValueError:
        print("Entrada invalida. Digite números inteiros.")

if __name__ == "__main__":
    main()
"""