from collections import deque


class Grafo:
    def __init__(self, nro_vertices: int, grau_max: int, eh_ponderado: bool):
        self.nro_vertices = nro_vertices
        self.grau_max = grau_max
        self.eh_ponderado = eh_ponderado

        # Listas para armazenar o grau de cada vértice, as arestas e os pesos
        self.grau = [0] * nro_vertices
        self.arestas = [[] for _ in range(nro_vertices)]
        self.pesos = [[] for _ in range(nro_vertices)] if eh_ponderado else None

    def insere_aresta(self, orig: int, dest: int, eh_digrafo: bool = False, peso: float = 0.0) -> bool:
        if orig < 0 or orig >= self.nro_vertices or dest < 0 or dest >= self.nro_vertices:
            return False

        # Verifica se respeita o limite do grau máximo informado na criação
        if self.grau[orig] >= self.grau_max:
            return False

        self.arestas[orig].append(dest)
        if self.eh_ponderado:
            self.pesos[orig].append(peso)
        self.grau[orig] += 1

        # Se não for dígrafo (grafo direcionado), insere a volta de forma recursiva
        if not eh_digrafo:
            self.insere_aresta(dest, orig, eh_digrafo=True, peso=peso)

        return True

    def remove_aresta(self, orig: int, dest: int, eh_digrafo: bool = False) -> bool:
        if orig < 0 or orig >= self.nro_vertices or dest < 0 or dest >= self.nro_vertices:
            return False

        if dest not in self.arestas[orig]:
            return False  # Elemento não encontrado

        idx = self.arestas[orig].index(dest)

        # Remove a aresta e o peso correspondente
        self.arestas[orig].pop(idx)
        if self.eh_ponderado:
            self.pesos[orig].pop(idx)
        self.grau[orig] -= 1

        if not eh_digrafo:
            self.remove_aresta(dest, orig, eh_digrafo=True)

        return True

    def imprime_grafo(self):
        for i in range(self.nro_vertices):
            print(f"{i}: ", end="")
            for j in range(self.grau[i]):
                if self.eh_ponderado:
                    print(f"{self.arestas[i][j]}({self.pesos[i][j]:.2f}), ", end="")
                else:
                    print(f"{self.arestas[i][j]}, ", end="")
            print()

    def _procura_menor_distancia(self, dist: list, visitado: list) -> int:
        menor = -1
        primeiro = True
        for i in range(self.nro_vertices):
            if dist[i] >= 0 and not visitado[i]:
                if primeiro:
                    menor = i
                    primeiro = False
                elif dist[menor] > dist[i]:
                    menor = i
        return menor

    def menor_caminho_grafo(self, ini: int):
        """Algoritmo de Dijkstra para encontrar o menor caminho."""
        cont = self.nro_vertices
        visitado = [False] * self.nro_vertices
        ant = [-1] * self.nro_vertices
        dist = [-1.0] * self.nro_vertices

        dist[ini] = 0.0

        while cont > 0:
            vert = self._procura_menor_distancia(dist, visitado)
            if vert == -1:
                break

            visitado[vert] = True
            cont -= 1

            for i in range(self.grau[vert]):
                ind = self.arestas[vert][i]
                peso_aresta = self.pesos[vert][i] if self.eh_ponderado else 1.0

                if dist[ind] < 0:
                    dist[ind] = dist[vert] + peso_aresta
                    ant[ind] = vert
                else:
                    if dist[ind] > dist[vert] + peso_aresta:
                        dist[ind] = dist[vert] + peso_aresta
                        ant[ind] = vert

        return ant, dist

    def _busca_profundidade(self, ini: int, visitado: list, cont: int):
        visitado[ini] = cont
        print(f"{ini} ", end="")

        for i in range(self.grau[ini]):
            vizinho = self.arestas[ini][i]
            if visitado[vizinho] == 0:
                self._busca_profundidade(vizinho, visitado, cont + 1)

    def busca_profundidade_grafo(self, ini: int):
        visitado = [0] * self.nro_vertices
        self._busca_profundidade(ini, visitado, cont=1)
        print()
        return visitado

    def busca_largura_grafo(self, ini: int):
        visitado = [0] * self.nro_vertices
        cont = 1

        # Utiliza o deque do Python que é otimizado para filas (FIFO)
        fila = deque()
        fila.append(ini)
        visitado[ini] = cont

        while fila:
            vert = fila.popleft()
            print(f"{vert} ", end="")
            cont += 1

            for i in range(self.grau[vert]):
                vizinho = self.arestas[vert][i]
                if visitado[vizinho] == 0:
                    fila.append(vizinho)
                    visitado[vizinho] = cont
        print()
        return visitado
