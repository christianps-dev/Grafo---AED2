import math

INF = 1e9


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
    """Monta e retorna a matriz de adjacência preenchida com as distâncias geométricas."""
    total_vertices = len(vertices)
    # Inicializa a matriz com valor infinito para indicar ausência de conexões
    matriz_adj = [[INF] * total_vertices for _ in range(total_vertices)]

    for art in arestas:
        a = art.orig
        b = art.dest
        distancia = calc_dist(vertices[a].x, vertices[a].y, vertices[b].x, vertices[b].y)
        matriz_adj[a][b] = distancia
        matriz_adj[b][a] = distancia  # Grafo não direcionado

    return matriz_adj


def dijkstra(matriz_adj: list, vertices: list, inicio: int, fim: int):
    total_vertices = len(vertices)
    dist = [INF] * total_vertices
    prev = [-1] * total_vertices
    visited = [False] * total_vertices

    dist[inicio] = 0.0

    for _ in range(total_vertices):
        # Encontra o vértice não visitado com a menor distância atualizada
        u = -1
        min_dist = INF
        for j in range(total_vertices):
            if not visited[j] and dist[j] < min_dist:
                u = j
                min_dist = dist[j]

        if u == -1:
            break

        visited[u] = True

        # Relaxamento das arestas vizinhas
        for v in range(total_vertices):
            if matriz_adj[u][v] < INF and dist[u] + matriz_adj[u][v] < dist[v]:
                dist[v] = dist[u] + matriz_adj[u][v]
                prev[v] = u

    if dist[fim] == INF:
        print(f"Sem caminho entre {inicio} e {fim}")
        return

    print(f"\nDistancia total: {dist[fim]:.2f} u. m.")

    # Reconstrói a rota de trás para frente seguindo os predecessores
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
    # Carga de dados idêntica à lista V do arquivo MenorCaminhoDijkstrav2.c
    v_dados = [
        (0, 149.0, 200.0), (1, 225.0, 200.0), (2, 156.175936, 193.978675),
        (3, 164.288446, 189.294915), (4, 173.091035, 186.091035), (5, 182.316240, 184.464382),
        (6, 191.683760, 184.464382), (7, 200.908965, 186.091035), (8, 209.711554, 189.294915),
        (9, 217.824064, 193.978675), (10, 217.824064, 206.021325), (11, 209.711554, 210.705085),
        (12, 200.908965, 213.908965), (13, 191.683760, 215.535618), (14, 182.316240, 215.535618),
        (15, 173.091035, 213.908965), (16, 164.288446, 210.705085), (17, 156.175936, 206.021325)
    ]
    vertices = [Vertice(d[0], d[1], d[2]) for d in v_dados]

    # Carga de dados idêntica à lista A do arquivo MenorCaminhoDijkstrav2.c
    a_dados = [
        (0, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 0),
        (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17), (17, 0)
    ]
    arestas = [Aresta(d[0], d[1]) for d in a_dados]

    total_vertices = len(vertices)
    total_arestas = len(arestas)

    matriz_adj = construir_grafo(vertices, arestas)

    print("Menor caminho entre dois vertices - algoritmo de Dijkstra\n")
    print(f"Total de vertices: {total_vertices}")
    print(f"Total de arestas : {total_arestas}")

    try:
        origem = int(input(f"Digite o vertice de origem (0 a {total_vertices - 1}): "))
        destino = int(input(f"Digite o vertice de destino (0 a {total_vertices - 1}): "))

        if 0 <= origem < total_vertices and 0 <= destino < total_vertices:
            dijkstra(matriz_adj, vertices, origem, destino)
        else:
            print("Indices invalidos.")
    except ValueError:
        print("Entrada invalida. Digite números inteiros.")


if __name__ == "__main__":
    main()