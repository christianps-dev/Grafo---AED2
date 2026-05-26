# Documentação Técnica: `conversor_osm.py`

## 1. Visão Geral do Ficheiro

O ficheiro `conversor_osm.py` é o **módulo de Engenharia de Dados** do sistema. A sua responsabilidade é atuar como uma ponte entre o mundo geográfico real (coordenadas de GPS esféricas) e o mundo computacional lógico (planos cartesianos em píxeis).

Ele ingere ficheiros brutos gerados pela comunidade OpenStreetMap (`.osm`, estruturados em XML), interpreta as ligações e regras de trânsito locais, aplica projeções cartográficas de nível industrial e exporta um ficheiro de texto limpo (`.poly`) pronto a ser consumido pelo motor de cálculo do Algoritmo de Dijkstra.

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
* Regista o `id_interno` (um índice sequencial de $0$ até $N$, crítico para a construção da Lista de Adjacência no passo seguinte).

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

A função `parse_osm(filename)` é o coração deste script. O seu ciclo de vida está dividido em 5 etapas rigorosas:

1. **Gestão de Caminhos (`Paths`)**
* Extrai apenas o nome do ficheiro (ex: `mapaUFG.osm` vira `mapaUFG`) e direcciona a saída obrigatoriamente para a pasta `../out/`.


2. **Extração de Vértices (`<node>`)**
* Varre todo o XML. Por cada nó que possua um ID e coordenadas, gera uma instância da classe `Node`, calcula o seu X e Y em UTM e regista este objeto num dicionário de tradução (`id_map`), permitindo que a pesquisa de "ID_Real -> ID_Sequencial" ocorra numa complexidade de tempo de $O(1)$.


3. **Interpretação de Vias e Regras de Trânsito (`<way>`)**
* Varre todas as vias presentes no ficheiro XML.
* **Análise de Direção:** Inspeciona as `tags` em busca da chave `oneway`.
* Se o valor for `yes`, `true` ou `1`, marca a via como mão única.
* Se o valor for `-1`, significa que o utilizador que desenhou o mapa no OSM traçou a via do fim para o princípio. O código de forma inteligente ativa a flag e **inverte a matriz de vértices** (`node_ids.reverse()`) para manter o sentido correto no grafo computacional.




4. **Tratamento Final do Eixo Y**
* Na cartografia, o "Norte" (Y positivo) aponta para cima. Contudo, em computação gráfica (Canvas, SVG), a origem `(0,0)` encontra-se no canto superior esquerdo e o eixo Y cresce para baixo.
* O script identifica o valor máximo de Y e inverte o eixo subtraindo todos os Y a esse máximo (`max_y - p.y`). Sem este passo, o mapa seria renderizado de pernas para o ar.


5. **Geração do Contrato Estático (`.poly`)**
* Escreve no disco o ficheiro resultante organizado em secções numéricas limpas:
* *Linha de Vértices:* Imprime o ID Interno e as coordenadas em formato `float` de 6 casas decimais (`{p.x:.6f}`).
* *Linha de Arestas:* Itera por cada par de vértices dentro de uma `Way` para gerar os segmentos de reta. Atribui a regra final (`1` para sentido único, `2` para duplo sentido).