import math
from .heap import Heap

# SE PRONUNCIA DI Á IS TRA 

INF = 1e9 # serve como um valor "nulo"

class Vertice:
    def __init__(self, v_id: int, x: float, y: float):
        self.id = v_id
        self.x = x
        self.y = y

class Aresta:
    def __init__(self, orig: int, dest: int):
        self.orig = orig
        self.dest = dest

def calc_dist(x0: float, y0: float, x1: float, y1: float) -> float:
    """Calcula a distância euclidiana entre dois pontos bidimensionais."""
    return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

def construir_grafo(vertices: list, arestas: list) -> list:
    """Monta e retorna a lista de adjacência preenchida com as distâncias geométricas."""
    total_vertices = len(vertices)
    lista_adj = [[] for _ in range (total_vertices)]
    for art in arestas:
        a = art.orig
        b = art.dest
        distancia = calc_dist(vertices[a].x, vertices[a].y, vertices[b].x, vertices[b].y)
        lista_adj[a].append((distancia, b))
        lista_adj[b].append((distancia, a))

    return lista_adj

def visualizar_lista_console(lista_adj: list):
    """Imprime a lista de adjacência formatada no console."""
    n = len(lista_adj)
    
    print("\n" + "=" * 65)
    print(" LISTA DE ADJACÊNCIA ".center(65))
    print("=" * 65)
    
    for i in range(n):
        print(f" Vértice {i:>2} |", end="")
        if not lista_adj[i]:
            print(" Sem conexões", end="")
        else:
            for distancia, destino in lista_adj[i]:
                print(f" ➔ (Dest: {destino:>2}, dist: {distancia:>5.1f})", end="")
        print() 
        
    print("=" * 65 + "\n")

def dijkstra(grafo: list, vertices: list, inicio: int, fim: int):
    total_vertices = len(vertices)
    dist = [INF] * total_vertices
    prev = [-1] * total_vertices

    dist[inicio] = 0.0

    # 1. Instancia a sua Fila de Prioridade e insere a origem
    minha_heap = Heap()
    minha_heap.insert((0.0, inicio))

    # 2. O laço roda enquanto houver caminhos para testar
    while not minha_heap.isEmpty():
        
        # 3. Extrai imediatamente o vértice mais próximo
        dist_atual, u = minha_heap.extractMin()

        # 4. Remoção Preguiçosa (Lazy Deletion)
        if dist_atual > dist[u]:
            continue

        # 5. Varre apenas os vizinhos reais na Lista de Adjacência
        for peso, v in grafo[u]:
            # Relaxamento da aresta
            if dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                prev[v] = u
                # 6. Insere o novo melhor caminho na Heap
                minha_heap.insert((dist[v], v))

    if dist[fim] == INF:
        print(f"Sem caminho entre {inicio} e {fim}")
        return

    print(f"\nDistancia total: {dist[fim]:.2f} u. m.")

    # Reconstrói a rota de trás para frente
    caminho = []
    v = fim
    while v != -1:
        caminho.append(v)
        v = prev[v]
    caminho.reverse()

    print("\nCaminho (do inicio ao fim):")
    for vert_id in caminho:
        print(f"{vert_id} (x={vertices[vert_id].x:.6f}, y={vertices[vert_id].y:.6f})")

def main():
    v_dados = [
        (0, 149.0, 200.0), (1, 225.0, 200.0), (2, 156.175936, 193.978675),
        (3, 164.288446, 189.294915), (4, 173.091035, 186.091035), (5, 182.316240, 184.464382),
        (6, 191.683760, 184.464382), (7, 200.908965, 186.091035), (8, 209.711554, 189.294915),
        (9, 217.824064, 193.978675), (10, 217.824064, 206.021325), (11, 209.711554, 210.705085),
        (12, 200.908965, 213.908965), (13, 191.683760, 215.535618), (14, 182.316240, 215.535618),
        (15, 173.091035, 213.908965), (16, 164.288446, 210.705085), (17, 156.175936, 206.021325)
    ]
    vertices = [Vertice(d[0], d[1], d[2]) for d in v_dados]
    
    a_dados = [
        (0, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 0),
        (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 0)
    ]
    arestas = [Aresta(d[0], d[1]) for d in a_dados]

    total_vertices = len(vertices)
    total_arestas = len(arestas)

    grafo = construir_grafo(vertices, arestas)
    visualizar_lista_console(grafo)
    
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
