import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
from djikstra_geometrico import carregar_mapa_poly, dijkstra,construir_grafo
from conversor_osm import parse_osm
from math import sqrt

class Janela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho de AED2")
        self.setGeometry(100, 100, 1200, 800)

        self.origem_selecionada = None
        self.destino_selecionado = None
        self.estado = None
        self.caminho_resultado = []
        
        arq_poly = "../out/mapaUFG.poly"
        self.vertices, self.arestas = carregar_mapa_poly(arq_poly)
        self.grafo = construir_grafo(self.vertices,self.arestas)
        
        self.mapa_vertices = {v.id: v for v in self.vertices}

        self.init_ui()
        self.desenhar_grafo()

    def init_ui(self):
        self.scene = QGraphicsScene()
        self.view = VisualizadorMapa(self.scene, self)

        self.painel = QVBoxLayout()
        
        self.lbl_titulo = QLabel("Algoritmo de Dijkstra")
        

        self.lbl_status = QLabel("Origem: Não selecionada<p>Destino: Não selecionado</p><p>Estado: Nulo</p>")
        
        
        self.lbl_estatisticas = QLabel("<b>Estatísticas:</b> <p>Tempo: -</p>"
                                       "<p>Nós explorados: -</p>"
                                       "<p>Custo: -</p>")

        self.btn_importar = QPushButton("Importar Mapa (.osm)")
        self.btn_importar.clicked.connect(self.importar_mapa)

        self.btn_calcular = QPushButton("Calcular Menor Caminho")
        self.btn_calcular.clicked.connect(self.calcular_caminho)

        self.btn_limpar = QPushButton("Desfazer Seleção")
        self.btn_limpar.clicked.connect(self.limpar_selecoes)


        self.painel.addWidget(self.lbl_titulo)
        self.painel.addWidget(self.btn_importar)
        self.painel.addWidget(self.lbl_status)
        self.painel.addWidget(self.btn_calcular)
        self.painel.addWidget(self.btn_limpar)
        self.painel.addWidget(self.lbl_estatisticas)
        self.painel.addStretch()

        layout_horizontal = QHBoxLayout()
        
        widget_lateral = QWidget()
        widget_lateral.setLayout(self.painel)
        layout_horizontal.addWidget(widget_lateral, stretch=2)

        layout_horizontal.addWidget(self.view, stretch=4)
        conteudo_central = QWidget()
        conteudo_central.setLayout(layout_horizontal)
        self.setCentralWidget(conteudo_central)
    
    def desenhar_grafo(self):
        self.scene.clear()

        dir_mao_dupla = QPen(QColor("#2980b9"), 2)
        dir_mao_unica = QPen(QColor("#16a085"), 2) 
        
        vertice_normal = QBrush(QColor("#e5e5e6"))
        vertice_origem = QBrush(QColor("#11ff00")) 
        vertice_destino = QBrush(QColor("#ff0000")) 

        for aresta in self.arestas:
            x1 = self.vertices[aresta.orig].x
            y1 = self.vertices[aresta.orig].y
            x2 = self.vertices[aresta.dest].x 
            y2 = self.vertices[aresta.dest].y
            dir = dir_mao_unica if aresta.tipo == 1 else dir_mao_dupla
            
            self.scene.addLine(x1, y1, x2, y2, dir)

        if self.caminho_resultado and len(self.caminho_resultado) > 1:
            pen_rota = QPen(QColor("#e67e22"), 4, Qt.PenStyle.SolidLine)
            
            for i in range(len(self.caminho_resultado) - 1):
                u = self.caminho_resultado[i]
                v = self.caminho_resultado[i + 1]

                v_u = self.mapa_vertices.get(u)
                v_v = self.mapa_vertices.get(v)

                if v_u and v_v:
                    self.scene.addLine(v_u.x, v_u.y, v_v.x, v_v.y, pen_rota)

        

        for vertice in self.vertices:
            vertice_tipo = vertice_normal
            tamanho = 10
            
            if vertice.id == self.origem_selecionada:
                vertice_tipo = vertice_origem
                tamanho = 14
            elif vertice.id == self.destino_selecionado:
                vertice_tipo = vertice_destino
                tamanho = 14
            
            self.scene.addEllipse(vertice.x - tamanho/2, vertice.y - tamanho/2, tamanho, tamanho, QPen(Qt.GlobalColor.black), vertice_tipo)

    def tratar_clique_mapa(self, x, y):
        proximidade_limite = 10.0
        vertice_proximo = None
        menor_distancia = float('inf')

        for vertice in self.vertices:
            dist = sqrt(((vertice.x - x) ** 2 + (vertice.y - y) ** 2))
            if dist < menor_distancia and dist < proximidade_limite:
                menor_distancia = dist
                vertice_proximo = vertice.id

        if vertice_proximo is not None:
            if self.origem_selecionada is None:
                self.origem_selecionada = vertice_proximo
            elif self.destino_selecionado is None and vertice_proximo != self.origem_selecionada:
                self.destino_selecionado = vertice_proximo
            
            self.atualizar_interface_status()
            self.desenhar_grafo()

    def atualizar_interface_status(self):
        origem_txt = f"<font color='green'><b>{self.origem_selecionada}</b></font>" if self.origem_selecionada else "Não selecionada"
        destino_txt = f"<font color='red'><b>{self.destino_selecionado}</b></font>" if self.destino_selecionado else "Não selecionado"
        self.lbl_status.setText(f"Origem: {origem_txt}<p>Destino: {destino_txt}</p><p>Estado: {self.estado}")

    def importar_mapa(self):
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Mapa", "", "Arquivos (*.osm)")
        print(f"Arquivo selecionado: {caminho_arquivo}")
        parse_osm(caminho_arquivo)

    def limpar_selecoes(self):
        self.origem_selecionada = None
        self.destino_selecionado = None
        self.estado = None
        self.atualizar_interface_status()
        self.caminho_resultado = []
        self.lbl_estatisticas.setText("<b>Estatísticas:</b>\nTempo: -\nNós explorados: -\nCusto: -")
        self.lbl_status.setText(f"Origem: {self.origem_selecionada}<p>Destino: {self.destino_selecionado}</p><p>Estado: {self.estado}")
        self.desenhar_grafo()

    def calcular_caminho(self):
        if (self.origem_selecionada is not None) and (self.destino_selecionado is not None):
            self.resultado = dijkstra(self.grafo,self.vertices,self.origem_selecionada,self.destino_selecionado)

            if self.resultado is not None:
                estatistica_teste = (f"<b>Estatísticas:</b><p>Tempo: - {self.resultado.get("tempo_ms", float)} ms</p>" +
                                              f"<p>Nós explorados: - {self.resultado.get("nos_explorados", float)} nós</p>"
                                              "<p>Custo: -</p>")
                self.estado = "Concluido"

                self.lbl_estatisticas.setText(estatistica_teste)

                self.caminho_resultado = self.resultado.get("caminho_ids", [])
                self.desenhar_grafo()
            else:
                self.estado = "Não Encontrado"

            self.atualizar_interface_status()


class VisualizadorMapa(QGraphicsView):
    def __init__(self, cena, pai):
        super().__init__(cena)
        self.pai = pai

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        fator_zoom = 1.20 if event.angleDelta().y() > 0 else 0.80
        self.scale(fator_zoom, fator_zoom)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            pos_cena = self.mapToScene(event.pos())
            self.pai.tratar_clique_mapa(pos_cena.x(), pos_cena.y())
        else:
            super().mousePressEvent(event)

    def calculo_caminho(self):
        self.resultado = dijkstra(self.grafo,self.vertices,self.origem_selecionada,self.destino_selecionado)
        caminho, tempo_ms, nos_explorados, dist_metros = self.resultado
        self.caminho_resultado = caminho

app = QApplication(sys.argv)
janela = Janela()
janela.show()
sys.exit(app.exec())