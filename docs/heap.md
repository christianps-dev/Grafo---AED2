---

# Min-Heap em Python para Algoritmo de Dijkstra

Esta é uma implementação customizada e otimizada de uma Fila de Prioridade (Min-Heap) construída do zero em Python. Ela foi projetada especificamente para servir como o "motor" do **Algoritmo de Dijkstra** ao trabalhar com **Listas de Adjacência**.

## Principais Características

* **Nativa para Tuplas:** A estrutura foi pensada para armazenar elementos no formato `(distancia, vertice)`. O Python avalia tuplas automaticamente pelo primeiro elemento, garantindo que o vértice mais próximo suba para o topo da árvore.
* **Remoção Preguiçosa (Lazy Deletion):** Em vez de implementar um método custoso de `deleteNode` $O(N)$ para atualizar rotas, esta Heap foi arquitetada para trabalhar com inserções redundantes. Caminhos mais curtos saem primeiro, e rotas antigas são ignoradas no loop principal, mantendo a performance impecável.
* **Tamanho O(1):** Utiliza a capacidade nativa de listas do Python (`len()`) para checagem de tamanho instantânea.
* **Sem dependências:** Implementada utilizando apenas Python puro, sem necessidade de importar módulos como `heapq` ou bibliotecas externas.

---

## API e Métodos

A classe `Heap` esconde a complexidade matemática da árvore binária através de métodos públicos simples:

### Métodos Principais

* **`insert(key: tuple)`** | Complexidade: $O(\log N)$
Adiciona um novo caminho à Fila de Prioridade e reorganiza a árvore (Heapify Up) para garantir que o menor elemento fique na raiz.
* **`extractMin() -> tuple`** | Complexidade: $O(\log N)$
Remove e retorna a tupla `(distancia, vertice)` que possui o menor valor de distância. Reorganiza a árvore (Heapify Down) automaticamente para o próximo uso.
* **`peekMin() -> tuple`** | Complexidade: $O(1)$
Retorna a tupla de menor distância sem removê-la da estrutura. Levanta erro se a heap estiver vazia.

### Utilitários

* **`isEmpty() -> bool`**: Retorna `True` se a estrutura estiver vazia, ou `False` caso contrário.
* **`size() -> int`**: Retorna a quantidade atual de nós na árvore.

*(Nota: Os métodos internos com prefixo `__` e de reordenação estrutural, como `heapifyUp` e `heapifyDown`, são abstraídos do usuário final).* 

---

## Exemplo de Uso (Contexto Dijkstra)

Veja como integrar a classe `Heap` dentro do laço principal do Algoritmo de Dijkstra:

```python
from sua_biblioteca import Heap

# 1. Inicializa a Heap e insere o vértice de origem
minha_heap = Heap()
origem = 0
distancias = [float('inf')] * total_vertices

# Insere a origem: (distância_acumulada, vértice_atual)
distancias[origem] = 0.0
minha_heap.insert((0.0, origem))

# 2. Loop principal de busca
while not minha_heap.isEmpty():
    # Extrai o caminho mais curto atual
    dist_atual, u = minha_heap.extractMin()
    
    # -----------------------------------------------------
    # ESTRATÉGIA DE LAZY DELETION (Remoção Preguiçosa)
    # Se essa distância que saiu da heap for maior que a
    # já registrada, é uma rota velha/ineficiente. Ignoramos.
    # -----------------------------------------------------
    if dist_atual > distancias[u]:
        continue
        
    # 3. Varre os vizinhos na Lista de Adjacência
    for peso, v in lista_adj[u]:
        nova_dist = dist_atual + peso
        
        # Se achou um caminho mais rápido, atualiza e joga na Heap
        if nova_dist < distancias[v]:
            distancias[v] = nova_dist
            minha_heap.insert((nova_dist, v))

```

## 🧠 Arquitetura de Memória e Índices

A árvore binária é achatada e armazenada em um array (lista do Python) contíguo na memória, utilizando as seguintes fórmulas matemáticas para navegação entre os nós:

* **Pai:** `(index - 1) // 2`
* **Filho Esquerdo:** `2 * index + 1`
* **Filho Direito:** `2 * index + 2`
