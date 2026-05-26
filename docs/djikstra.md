# Documentação: Algoritmo de Dijkstra e Estruturas Base

Este documento detalha a implementação do algoritmo de busca de menor caminho (Dijkstra) e as estruturas de dados fundamentais para a representação do grafo em memória. O código atende à responsabilidade de implementar a lógica de busca e otimização , utilizando uma fila de prioridade baseada em Heap Mínima.

## 1. Módulos e Constantes

* **`math`**: Utilizado para o cálculo de raízes quadradas na distância euclidiana.

* **`Heap`**: Módulo customizado importado localmente (`from .heap import Heap`) que fornece a estrutura de Fila de Prioridade, garantindo eficiência na extração do vértice mais próximo.


* **`INF`**: Constante definida como `1e9` (1 bilhão) que atua como o valor representativo de "infinito" para inicializar as distâncias dos vértices.

---

## 2. Modelagem de Dados

A base do sistema é construída sobre duas classes principais para representar as entidades geométricas e lógicas do mapa:

| Classe | Atributos | Descrição |
| --- | --- | --- |
| **`Vertice`** | `id` (int), `x` (float), `y` (float) | Representa um ponto no mapa geográfico. Armazena um identificador único e as coordenadas espaciais. |
| **`Aresta`** | `orig` (int), `dest` (int) | Representa uma conexão (rua/via) entre dois vértices, utilizando seus respectivos identificadores. |

---

## 3. Funções de Apoio e Estruturação

### `calc_dist(x0, y0, x1, y1) -> float`

Calcula a distância euclidiana geométrica entre dois pontos bidimensionais.
**Fórmula Matemática:**
$d = \sqrt{(x_0 - x_1)^2 + (y_0 - y_1)^2}$

### `construir_grafo(vertices: list, arestas: list) -> list`

Converte as listas brutas de vértices e arestas em uma **Lista de Adjacência**, que é a estrutura ideal para lidar com grafos esparsos de forma eficiente.

* **Processo:** Itera sobre as arestas, calcula a distância real entre a origem e o destino usando `calc_dist`, e popula a lista bidimensional.
* **Nota de Comportamento:** Atualmente, a função insere a conexão em ambos os sentidos (mão dupla).

### `visualizar_lista_console(lista_adj: list)`

Gera uma representação visual formatada da lista de adjacência diretamente no terminal, facilitando o debug e a validação das conexões geométricas.

---

## 4. Algoritmo Principal

### `dijkstra(grafo: list, vertices: list, inicio: int, fim: int)`

Calcula a rota indicativa do menor caminho entre dois vértices, imprimindo as coordenadas passo a passo.

**Etapas de Execução:**

1. **Inicialização:** Cria um vetor de distâncias (`dist`) inicializado com `INF` e um vetor de predecessores (`prev`) inicializado com `-1`. A distância do vértice de início é definida como `0.0`.


2. **Fila de Prioridade:** Instancia a `Heap` mínima e insere o vértice de origem.


3. **Busca e Relaxamento:** Enquanto a fila não estiver vazia, o vértice com menor distância acumulada é extraído. O algoritmo varre todos os seus vizinhos reais e atualiza (relaxa) o custo do caminho se encontrar uma rota mais vantajosa.


4. **Remoção Preguiçosa (Lazy Deletion):** Otimização que ignora vértices extraídos da Heap se a distância atual registrada for maior do que a já confirmada no vetor de distâncias. Isso evita sobrecarga de memória.


5. **Reconstrução de Rota:** Utiliza o vetor de predecessores para rastrear o caminho do destino até a origem, invertendo a lista no final para exibir o trajeto ordenado.

---

## 5. Fluxo de Execução (`main`)

A função principal do script executa as seguintes operações para fins de teste isolado (mock):

1. Instancia `18` vértices fictícios com coordenadas flutuantes.
2. Instancia `18` arestas conectando os vértices em um formato poligonal fechado.
3. Constrói a lista de adjacência e a imprime no terminal.
4. Solicita ao usuário (via CLI) os nós de origem e destino, validando os limites (0 a 17).
5. Aciona a função `dijkstra` para processamento e exibição textual do menor caminho.