# Documentação Técnica: `conversor_osm.py`

## 1. Visão Geral do Ficheiro

O ficheiro `conversor_osm.py` é o **módulo de Engenharia de Dados e Otimização** do sistema. A sua responsabilidade é atuar como uma ponte entre o mundo geográfico real (coordenadas de GPS esféricas) e o mundo computacional lógico (planos cartesianos em píxeis).

Ele ingere ficheiros brutos gerados pela comunidade OpenStreetMap (`.osm`, estruturados em XML), filtra ruído de dados (edifícios, rios, limites territoriais), interpreta as ligações e regras de trânsito locais, aplica projeções cartográficas de nível industrial e exporta um ficheiro de texto limpo e conciso (`.poly`), pronto a ser consumido de forma ultra-rápida pelo motor de cálculo do Algoritmo de Dijkstra.

---

## 2. Dependências e Parâmetros Geodésicos

### Módulos Nativos e Globais

* **`xml.etree.ElementTree as ET`**: Biblioteca nativa de Python extremamente segura e rápida para varrer (fazer o *parsing*) de árvores XML sem a necessidade de manipular strings manualmente.
* **`math`**: Utilizado para conversões trigonométricas (seno, cosseno, tangentes e radianos) essenciais na projeção geográfica.
* **`FATOR_ESCALA`**: Constante importada do ficheiro `config.py` para garantir que o nível de zoom visual aplicado à extração é idêntico ao fator multiplicativo utilizado no backend do Dijkstra.

### Constantes do Modelo WGS84 e UTM

O código utiliza o modelo **WGS84** (World Geodetic System 1984), o mesmo modelo matemático utilizado pelos satélites GPS modernos:

* **`A_WGS84 = 6378137.0`**: Representa o raio equatorial da Terra em metros.
* **`F_WGS84`**: Fator de achatamento dos polos.
* **`K0 = 0.9996`**: Fator de escala no meridiano central para a projeção UTM.
* **`LON0_DEG = -45.0`**: Longitude do meridiano central da **Zona UTM 23S** (que abrange regiões do Brasil como Goiás).

---

## 3. Estruturas de Memória (Classes)

O script constrói o mapa temporariamente na memória através de duas entidades:

### Classe `Node` (Nó / Vértice)

* Armazena o `id_original` providenciado pelo OpenStreetMap (que costumam ser números gigantescos).
* Armazena a `lat` (Latitude) e `lon` (Longitude) brutas.
* Inicializa variáveis `x` e `y` para receber a coordenada planificada.
* Regista o `id_interno` (um índice sequencial de $0$ até $N$, crítico para a construção da Lista de Adjacência no passo seguinte). Este ID agora é atribuído de forma tardia, garantindo que apenas nós válidos o recebam.

### Classe `Way` (Caminho / Via)

* **`node_ids`**: Uma matriz que regista a sequência de vértices que compõem uma rua.
* **`is_oneway`**: Um identificador booleano (verdadeiro/falso) que dita se a rua tem um sentido de trânsito único.

---

## 4. O Motor Matemático de Projeção

### 4.1. `converter_para_utm(lat_deg, lon_deg)`

Esta função traduz uma localização esférica na curvatura da Terra numa coordenada num plano 2D continuo.

* **Mecânica:** Transforma os graus em radianos e aplica a sequência de polinómios complexos de série de Taylor para expandir as coordenadas leste (`x`) e norte (`y`).
* **Correção Hemisférica:** Se a latitude for negativa (Hemisfério Sul), a função adiciona $10.000.000,0$ ao eixo Y para impedir a existência de coordenadas negativas que corromperiam o desenho em ecrã.

### 4.2. `reduzir_escala(pontos, redutor)`

Esta função atua como uma "câmara" que enquadra o mapa gerado.

* Procura a menor coordenada `x` e a menor `y` do mapa, subtraindo esse valor a todos os vértices. Este processo "arrasta" o mapa para colar a extremidade superior esquerda à origem `(0,0)`.
* Divide os valores resultantes pelo `FATOR_ESCALA`, reduzindo o número de píxeis absolutos que o ecrã terá de renderizar.

---

## 5. Fluxo de Execução Principal (`parse_osm`)

A função `parse_osm(filename)` é o coração deste script. O seu ciclo de vida foi otimizado para evitar a retenção de dados inúteis e está dividido em 5 etapas rigorosas:

1. **Gestão de Caminhos (`Paths`) e Indexação Geográfica Preliminar**

* Extrai apenas o nome do ficheiro (ex: `mapaUFG.osm` vira `mapaUFG`) e direciona a saída obrigatoriamente para a pasta `../out/`.
* Varre os `<node>` do XML e cria um dicionário temporário (`all_nodes_temp`) contendo apenas os IDs reais e as coordenadas (sem executar conversões pesadas numa primeira fase).

2. **Filtragem Topológica e Interpretação de Vias (`<way>`)**

* Varre todas as vias presentes no ficheiro XML. Este é o **ponto crítico de otimização**.
* **Filtro de Ruído:** O código procura a chave `highway` e valida se o seu valor pertence a um leque estrito de vias motorizadas (`motorway`, `residential`, `primary`, etc.). Se a via for uma vedação, um edifício ou um rio, é sumariamente descartada.
* **Análise de Direção:** Inspeciona a chave `oneway`. Se o valor for `yes` ou `1`, marca como mão única. Se for `-1`, inverte inteligentemente a matriz de vértices (`node_ids.reverse()`) para corrigir a topologia vetorial da via no grafo computacional.
* Guarda os IDs dos nós que fazem parte destas vias válidas num *Set* de memória (`nos_utilizados_ids`).

3. **Mapeamento Tardio e Projeção (Eliminação de Nós Órfãos)**

* Após descobrir quais são os nós que *realmente importam* para o trânsito, o sistema recupera as suas latitudes e longitudes, calcula a projeção matemática (`converter_para_utm`) e gera instâncias da classe `Node`.
* Aqui, é-lhes atribuído um `id_interno` puramente sequencial (de $0$ a $N$), preenchendo o dicionário de tradução final (`id_map`) em tempo $O(1)$. Árvores e semáforos órfãos ficam de fora do grafo.

4. **Tratamento Final do Eixo Y**

* Na cartografia, o "Norte" (Y positivo) aponta para cima. Contudo, em computação gráfica (Canvas, SVG), a origem `(0,0)` encontra-se no canto superior esquerdo e o eixo Y cresce para baixo.
* O script identifica o valor máximo de Y e inverte o eixo subtraindo todos os Y a esse máximo (`max_y - p.y`). Sem este passo, o mapa seria renderizado de pernas para o ar.

5. **Geração do Contrato Estático (`.poly`)**

* Escreve no disco o ficheiro resultante organizado em secções numéricas rigorosas e livres de ruído:
* *Linha de Vértices:* Imprime o ID Interno e as coordenadas em formato `float` de 6 casas decimais (`{p.x:.6f}`).
* *Linha de Arestas:* Itera por cada par de vértices dentro de uma `Way` válida para gerar os segmentos de reta. Mapeia de volta os IDs reais para os novos IDs sequenciais, e atribui a regra de trânsito final (`1` para sentido único, `2` para duplo sentido).