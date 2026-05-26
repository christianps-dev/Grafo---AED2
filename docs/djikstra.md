# Documentação Técnica: `djikstra_geometrico.py`

## 1. Visão Geral do Ficheiro

O ficheiro `djikstra_geometrico.py` atua como o **motor matemático e lógico** do sistema de navegação espacial. O seu propósito central é carregar dados geográficos planificados, estruturá-los na memória do computador e calcular a rota mais eficiente (menor caminho) entre dois pontos utilizando o **Algoritmo de Dijkstra**.

Este módulo foi desenhado para ser consumido por outros ficheiros (como um ficheiro `main.py` integrador), motivo pelo qual o seu bloco de execução direta (`main()`) encontra-se comentado no final do código.

---

## 2. Dependências e Configurações Globais

### Módulos Importados

* **`math`**: Fornece a função `sqrt` para o cálculo da raiz quadrada na fórmula de distância euclidiana.
* **`time`**: Fornece `perf_counter` para medição de alta precisão (em milissegundos) do tempo de execução do algoritmo.
* **`Heap` (Local)**: Estrutura de dados de Fila de Prioridade (Min-Heap) importada do ficheiro `heap.py`. É crucial para garantir a eficiência $O((V + E) \log V)$ do algoritmo.
* **`FATOR_ESCALA` (Local)**: Variável importada do ficheiro `config.py`, utilizada para converter a distância em píxeis (ecrã) para a distância real (metros).

### Constantes

* **`INF = 1e9`**: Representa um valor infinitamente grande (mil milhões) utilizado para inicializar as distâncias desconhecidas no grafo antes da avaliação.

---

## 3. Estruturas de Dados (Classes)

O código utiliza programação orientada a objetos para tipar e organizar os elementos do mapa cartográfico:

### Classe `Vertice`

Representa um ponto ou cruzamento no mapa cartográfico.

* **`id` (int)**: Identificador único numérico do vértice.
* **`x` (float)**: Coordenada no eixo X (leste-oeste).
* **`y` (float)**: Coordenada no eixo Y (norte-sul).

### Classe `Aresta`

Representa uma via ou rua que liga dois vértices.

* **`orig` (int)**: Identificador do vértice de origem.
* **`dest` (int)**: Identificador do vértice de destino.
* **`tipo` (int)**: Regra de trânsito associada à via. Recebe `1` para via de sentido único (mão única) ou `2` para via de dois sentidos (mão dupla).

---

## 4. Funções Principais

### 4.1. `calc_dist(x0, y0, x1, y1) -> float`

Calcula a distância em linha reta (Euclidiana) entre dois pontos num plano bidimensional bidimensional. Atua como a função de custo/peso para as arestas do grafo.

* **Matemática Aplicada**: Utiliza o Teorema de Pitágoras: $d = \sqrt{(x_0 - x_1)^2 + (y_0 - y_1)^2}$.

### 4.2. `construir_grafo(vertices: list, arestas: list) -> list`

Converte as listas lineares de vértices e arestas numa **Lista de Adjacência**, otimizada para o consumo do algoritmo de Dijkstra.

* **Processamento de Custo**: Calcula automaticamente o peso da aresta através da função `calc_dist` invocada com as coordenadas em tempo real.
* **Lógica Direcional (Controlo de Fluxo)**:
* A ligação da origem para o destino (`A -> B`) é **sempre** adicionada.
* A ligação reversa (`B -> A`) **apenas** é adicionada se o atributo `tipo` da aresta for igual a `2` (indicando permissão de mão dupla). Isto confere ao grafo a capacidade de respeitar as regras de trânsito da topologia real.



### 4.3. `carregar_mapa_poly(caminho_arquivo)`

Efetua o *parsing* (leitura e interpretação) de um ficheiro de texto estruturado com a extensão `.poly`.

* **Fluxo de Leitura**:
1. Abre o ficheiro e lê todas as linhas.
2. Extrai o número total de vértices a partir do cabeçalho inicial.
3. Itera pelas linhas seguintes para instanciar os objetos da classe `Vertice`.
4. Localiza o número total de arestas e continua a iteração para instanciar a classe `Aresta`. Note-se a captura obrigatória da 4.ª coluna (`dados[3]`) que define o `tipo` da via.


* **Retorno**: Um tuplo contendo a lista de instâncias de vértices e arestas `(vertices, arestas)`.

---

## 5. O Núcleo: `dijkstra(grafo, vertices, inicio, fim)`

Esta é a função central que executa o cálculo de rotas. Foi desenhada tendo em conta o desempenho elevado e a recolha de métricas de execução.

### Fluxo de Execução do Algoritmo:

1. **Inicialização**:
* Cria o vetor de distâncias (`dist`) inicializado a "infinito" (`INF`), à exceção da origem (distância `0.0`).
* Cria o vetor de predecessores (`prev`) inicializado a `-1` para rastreamento posterior do caminho.


2. **Ciclo de Busca (Min-Heap)**:
* Extrai sucessivamente o nó mais próximo da Fila de Prioridade (`Heap`).
* Aplica a otimização de **Lazy Deletion** (Remoção Preguiçosa): se a distância extraída for maior que a distância registada em `dist`, o nó é ignorado.
* Regista o incremento de nós explorados (`nos_explorados += 1`).
* Efetua o **relaxamento** das arestas adjacentes: verifica se o caminho atualizado custa menos do que o conhecimento anterior. Se sim, atualiza a matriz e introduz o novo valor na Fila de Prioridade.


3. **Pós-processamento e Métricas**:
* O relógio de precisão (`perf_counter`) regista o momento exato em que o algoritmo conclui a tarefa.
* Valida a existência do caminho (se o destino continuar como `INF`, retorna a falha na rota).
* Converte a distância lógica (píxeis baseados em coordenadas) para distância real no mundo (metros) multiplicando pelo `FATOR_ESCALA`.


4. **Reconstrução da Rota**:
* Utiliza a matriz de predecessores (`prev`) do fim até à origem e inverte a matriz (`caminho.reverse()`) para fornecer a ordem correta das direções.


5. **Apresentação e Retorno (Interface / API)**:
* Imprime no ecrã um relatório completo da execução (tempos, nós iterados e custos lógicos e reais).
* **Retorno Funcional**: Exporta e devolve um dicionário (JSON-like) contendo todas as variáveis cruciais (`caminho_ids`, `distancia_pixels`, `distancia_metros`, `nos_explorados`, `tempo_ms`). Isto permite que qualquer interface gráfica utilize estes dados para desenhar e apresentar a solução visualmente sem acoplar a lógica à interface.



---

## 6. Secção Comentada (Testes Históricos)

No final do ficheiro, existe uma função `main()` encapsulada entre triplas aspas `"""`. Este código serviu para testes em consola durante o desenvolvimento (solicitando *inputs* textuais de nó de origem e nó de destino, e efetuando tratamento de exceções `ValueError`). Como o sistema evoluiu para uma arquitetura modular acionada por um integrador externo, este bloco foi corretamente isolado para não interferir nas importações em produção.