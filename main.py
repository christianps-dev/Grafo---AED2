from grafo import Grafo

def main():
    eh_digrafo = False

    # Cria um grafo com 5 vértices, grau máximo 5 e não ponderado
    gr = Grafo(nro_vertices=5, grau_max=5, eh_ponderado=False)

    # Insere as arestas baseadas no main.c original
    gr.insere_aresta(0, 1, eh_digrafo)  # 1 2
    gr.insere_aresta(0, 4, eh_digrafo)  # 1 5
    gr.insere_aresta(1, 2, eh_digrafo)  # 2 3
    gr.insere_aresta(1, 3, eh_digrafo)  # 2 4
    gr.insere_aresta(1, 4, eh_digrafo)  # 2 5
    gr.insere_aresta(2, 3, eh_digrafo)  # 3 4
    gr.insere_aresta(3, 4, eh_digrafo)  # 4 5

    print("Lista de adjacência ref. ao grafo:")
    gr.imprime_grafo()

    print("\nBusca em profundidade:")
    gr.busca_profundidade_grafo(0)

    print("\nBusca em largura:")
    gr.busca_largura_grafo(0)


if __name__ == "__main__":
    main()
